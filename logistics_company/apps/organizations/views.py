import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Office, Company
from apps.common.models import Address


def is_admin_or_manager(user):
    if user.is_superuser or user.role == "ADMIN":
        return True
    if hasattr(user, "employee_profile"):
        return user.employee_profile.employee_type == "MANAGER"
    return False


@login_required
def offices(request):
    return render(request, "organizations/offices.html")


@login_required
@require_http_methods(["GET"])
def offices_api_list(request):
    offices_qs = Office.objects.select_related("company", "address").order_by("name")

    data = [
        {
            "id": o.pk,
            "name": o.name,
            "code": o.code,
            "phone": o.phone or "",
            "working_hours": o.working_hours or "",
            "company_id": o.company_id,
            "company_name": o.company.name if o.company else "",
            "address_id": o.address_id,
            "address": str(o.address) if o.address else "",
            "address_city": o.address.city if o.address else "",
            "address_street": o.address.street if o.address else "",
        }
        for o in offices_qs
    ]

    companies = Company.objects.all().order_by("name")
    companies_data = [{"id": c.pk, "name": c.name} for c in companies]

    return JsonResponse({
        "success": True,
        "offices": data,
        "companies": companies_data,
    })


@login_required
@require_http_methods(["POST"])
def offices_api_create(request):
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    required = ["name", "code", "company_id"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}, status=400)

    if Office.objects.filter(code=data["code"]).exists():
        return JsonResponse({"success": False, "error": "Office code already exists."}, status=400)

    try:
        company = Company.objects.get(pk=data["company_id"])
    except Company.DoesNotExist:
        return JsonResponse({"success": False, "error": "Company not found."}, status=400)

    try:
        with transaction.atomic():
            address_data = data.get("address", {})
            if address_data:
                address, _ = Address.objects.get_or_create(
                    country=address_data.get("country", "Bulgaria"),
                    city=address_data.get("city", ""),
                    postal_code=address_data.get("postal_code", ""),
                    street=address_data.get("street", ""),
                    defaults={"details": address_data.get("details", "")}
                )
            elif data.get("address_id"):
                address = get_object_or_404(Address, pk=data["address_id"])
            else:
                return JsonResponse({"success": False, "error": "Address is required."}, status=400)

            office = Office.objects.create(
                company=company,
                name=data["name"],
                code=data["code"],
                phone=data.get("phone", ""),
                address=address,
                working_hours=data.get("working_hours", ""),
            )

        return JsonResponse({
            "success": True,
            "office": {
                "id": office.pk,
                "name": office.name,
                "code": office.code,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["PUT", "PATCH"])
def offices_api_update(request, office_id):
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    office = get_object_or_404(Office, pk=office_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    try:
        with transaction.atomic():
            if "name" in data:
                office.name = data["name"]
            if "code" in data:
                if Office.objects.filter(code=data["code"]).exclude(pk=office.pk).exists():
                    return JsonResponse({"success": False, "error": "Office code already exists."}, status=400)
                office.code = data["code"]
            if "phone" in data:
                office.phone = data["phone"]
            if "working_hours" in data:
                office.working_hours = data["working_hours"]
            if "company_id" in data:
                try:
                    office.company = Company.objects.get(pk=data["company_id"])
                except Company.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Company not found."}, status=400)

            address_data = data.get("address")
            if address_data:
                address, _ = Address.objects.get_or_create(
                    country=address_data.get("country", "Bulgaria"),
                    city=address_data.get("city", ""),
                    postal_code=address_data.get("postal_code", ""),
                    street=address_data.get("street", ""),
                    defaults={"details": address_data.get("details", "")}
                )
                office.address = address

            office.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def offices_api_delete(request, office_id):
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    office = get_object_or_404(Office, pk=office_id)

    if office.employees.exists():
        return JsonResponse({
            "success": False,
            "error": "Cannot delete office with assigned employees. Reassign employees first."
        }, status=400)

    try:
        office.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
