import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Employee
from apps.accounts.models import User, UserRole
from apps.organizations.models import Office


def employee_or_admin_required(view_func):
    """Decorator that requires user to be an employee, admin, or superuser."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        if request.user.is_superuser or request.user.role in ("ADMIN", "EMPLOYEE"):
            return view_func(request, *args, **kwargs)
        return JsonResponse({"error": "Permission denied."}, status=403)
    return _wrapped_view


def is_admin_or_manager(user):
    """Check if user has admin or manager permissions."""
    if user.is_superuser or user.role == "ADMIN":
        return True
    if hasattr(user, "employee_profile"):
        return user.employee_profile.employee_type == "MANAGER"
    return False


@login_required
def employees(request):
    return render(request, "employees/employees.html")


@login_required
@employee_or_admin_required
def employees_report(request):
    """Return all employees with their details."""
    employees_qs = Employee.objects.select_related(
        "user",
        "office"
    ).all().order_by("user__first_name", "user__last_name")

    data = [
        {
            "id": emp.pk,
            "employee_code": emp.employee_code,
            "username": emp.user.username,
            "first_name": emp.user.first_name,
            "last_name": emp.user.last_name,
            "email": emp.user.email,
            "phone": emp.user.phone or "-",
            "employee_type": emp.employee_type,
            "employee_type_display": emp.get_employee_type_display(),
            "office_id": emp.office_id,
            "office": str(emp.office) if emp.office else "-",
            "hire_date": emp.hire_date.strftime("%Y-%m-%d") if emp.hire_date else "-",
            "salary": float(emp.salary),
        }
        for emp in employees_qs
    ]

    return JsonResponse({
        "employees_count": len(data),
        "employees": data,
    })


@login_required
@require_http_methods(["GET"])
def employees_api_list(request):
    """API to list all employees."""
    employees_qs = Employee.objects.select_related("user", "office").order_by("user__first_name")

    data = [
        {
            "id": emp.pk,
            "employee_code": emp.employee_code,
            "username": emp.user.username,
            "first_name": emp.user.first_name,
            "last_name": emp.user.last_name,
            "email": emp.user.email,
            "phone": emp.user.phone or "",
            "employee_type": emp.employee_type,
            "office_id": emp.office_id,
            "office_name": str(emp.office) if emp.office else "",
            "hire_date": emp.hire_date.strftime("%Y-%m-%d") if emp.hire_date else "",
            "salary": float(emp.salary),
        }
        for emp in employees_qs
    ]

    offices = Office.objects.all().order_by("name")
    offices_data = [{"id": o.pk, "name": o.name, "code": o.code} for o in offices]

    return JsonResponse({
        "success": True,
        "employees": data,
        "offices": offices_data,
        "employee_types": [
            {"value": "COURIER", "label": "Courier"},
            {"value": "OFFICE", "label": "Office"},
            {"value": "MANAGER", "label": "Manager"},
        ]
    })


@login_required
@require_http_methods(["POST"])
def employees_api_create(request):
    """API to create a new employee."""
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    required = ["username", "email", "first_name", "last_name", "employee_code", "employee_type", "hire_date", "salary"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}, status=400)

    if User.objects.filter(username=data["username"]).exists():
        return JsonResponse({"success": False, "error": "Username already exists."}, status=400)

    if User.objects.filter(email=data["email"]).exists():
        return JsonResponse({"success": False, "error": "Email already exists."}, status=400)

    if Employee.objects.filter(employee_code=data["employee_code"]).exists():
        return JsonResponse({"success": False, "error": "Employee code already exists."}, status=400)

    if data["employee_type"] not in ["COURIER", "OFFICE", "MANAGER"]:
        return JsonResponse({"success": False, "error": "Invalid employee type."}, status=400)

    try:
        hire_date = datetime.strptime(data["hire_date"], "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid hire date format. Use YYYY-MM-DD."}, status=400)

    try:
        salary = Decimal(str(data["salary"]))
        if salary <= 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        return JsonResponse({"success": False, "error": "Invalid salary."}, status=400)

    office = None
    if data.get("office_id"):
        try:
            office = Office.objects.get(pk=data["office_id"])
        except Office.DoesNotExist:
            return JsonResponse({"success": False, "error": "Office not found."}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data.get("password", "employee123"),
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data.get("phone", ""),
                role=UserRole.EMPLOYEE,
            )

            employee = Employee.objects.create(
                user=user,
                employee_code=data["employee_code"],
                employee_type=data["employee_type"],
                office=office,
                hire_date=hire_date,
                salary=salary,
            )

        return JsonResponse({
            "success": True,
            "employee": {
                "id": employee.pk,
                "employee_code": employee.employee_code,
                "username": user.username,
                "email": user.email,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["PUT", "PATCH"])
def employees_api_update(request, employee_id):
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    employee = get_object_or_404(Employee, pk=employee_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    user = employee.user

    try:
        with transaction.atomic():
            if "first_name" in data:
                user.first_name = data["first_name"]
            if "last_name" in data:
                user.last_name = data["last_name"]
            if "email" in data:
                if User.objects.filter(email=data["email"]).exclude(pk=user.pk).exists():
                    return JsonResponse({"success": False, "error": "Email already exists."}, status=400)
                user.email = data["email"]
            if "phone" in data:
                user.phone = data["phone"]
            if "password" in data and data["password"]:
                user.set_password(data["password"])
            user.save()

            if "employee_code" in data:
                if Employee.objects.filter(employee_code=data["employee_code"]).exclude(pk=employee.pk).exists():
                    return JsonResponse({"success": False, "error": "Employee code already exists."}, status=400)
                employee.employee_code = data["employee_code"]

            if "employee_type" in data:
                if data["employee_type"] not in ["COURIER", "OFFICE", "MANAGER"]:
                    return JsonResponse({"success": False, "error": "Invalid employee type."}, status=400)
                employee.employee_type = data["employee_type"]

            if "office_id" in data:
                if data["office_id"]:
                    try:
                        employee.office = Office.objects.get(pk=data["office_id"])
                    except Office.DoesNotExist:
                        return JsonResponse({"success": False, "error": "Office not found."}, status=400)
                else:
                    employee.office = None

            if "hire_date" in data:
                try:
                    employee.hire_date = datetime.strptime(data["hire_date"], "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"success": False, "error": "Invalid hire date format."}, status=400)
                
            if "salary" in data:
                try:
                    employee.salary = Decimal(str(data["salary"]))
                except (InvalidOperation, ValueError):
                    return JsonResponse({"success": False, "error": "Invalid salary."}, status=400)
                
            employee.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def employees_api_delete(request, employee_id):
    if not is_admin_or_manager(request.user):
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    employee = get_object_or_404(Employee, pk=employee_id)
    user = employee.user

    try:
        with transaction.atomic():
            employee.delete()
            user.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
