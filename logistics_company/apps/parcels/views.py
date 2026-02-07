import json
import uuid
from decimal import Decimal, InvalidOperation
from functools import wraps
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .models import Parcel, ParcelStatus, ParcelStatusHistory
from apps.workforce.models import Employee
from apps.accounts.models import User, UserRole
from apps.organizations.models import Company, Office
from apps.common.models import Tariff, DeliveryType


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


@login_required
@employee_or_admin_required
def client_parcels_report(request, client_id=None, role="all"):
    """
    role: 'sent' -> sender
          'received' -> receiver
          'all' -> all parcels
    """
    parcels = Parcel.objects.select_related(
        "company",
        "sender",
        "receiver",
        "current_status",
        "sender_office",
        "receiver_office",
        "pickup_address",
        "delivery_address",
        "tariff",
    ).order_by("-created_at")

    client = None
    if role == "sent":
        if client_id is None:
            return JsonResponse({"error": "client_id is required for sent parcels"}, status=400)
        client = get_object_or_404(User, pk=client_id, role=UserRole.CLIENT)
        parcels = parcels.filter(sender=client)
    elif role == "received":
        if client_id is None:
            return JsonResponse({"error": "client_id is required for received parcels"}, status=400)
        client = get_object_or_404(User, pk=client_id, role=UserRole.CLIENT)
        parcels = parcels.filter(receiver=client)
    elif role == "all":
        pass
    else:
        return JsonResponse({"error": "Invalid role"}, status=400)

    data = [
        {
            "tracking_number": p.tracking_number,
            "status": p.current_status.name if p.current_status else "-",
            "delivery_type": p.get_delivery_type_display(),
            "price": float(p.price),
            "weight_kg": float(p.weight_kg),
            "sender": f"{p.sender.first_name} {p.sender.last_name}" if p.sender else "-",
            "receiver": f"{p.receiver.first_name} {p.receiver.last_name}" if p.receiver else "-",
            "sender_office": str(p.sender_office) if p.sender_office else "-",
            "receiver_office": str(p.receiver_office) if p.receiver_office else "-",
            "pickup_address": str(p.pickup_address) if p.pickup_address else "-",
            "delivery_address": str(p.delivery_address) if p.delivery_address else "-",
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": p.delivered_at.strftime("%Y-%m-%d %H:%M") if p.delivered_at else "-",
        }
        for p in parcels
    ]

    return JsonResponse({
        "client_id": client.id if client else None,
        "client_name": f"{client.first_name} {client.last_name}" if client else "All Clients",
        "parcels_count": parcels.count(),
        "parcels": data,
    })



@login_required
def parcels(request):
    user = request.user

    is_employee = user.is_superuser or user.role in ("ADMIN", "EMPLOYEE")
    can_register_parcel = is_employee

    if is_employee:
        parcels_qs = Parcel.objects.all()
    else:
        parcels_qs = Parcel.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )

    parcels_qs = parcels_qs.select_related(
        "company",
        "sender",
        "receiver",
        "pickup_address",
        "delivery_address",
        "current_status",
        "registered_by",
        "tariff",
        "sender_office",
        "receiver_office",
    ).order_by("-created_at")

    return render(
        request,
        "parcels/parcels.html",
        {
            "parcels": parcels_qs,
            "can_register_parcel": can_register_parcel,
        },
    )


@login_required
@employee_or_admin_required
def parcels_by_employee_report(request, employee_id=None):
    """Return all parcels registered by a specific employee."""

    parcels_qs = Parcel.objects.select_related(
        "sender",
        "receiver",
        "current_status",
        "sender_office",
        "receiver_office",
        "pickup_address",
        "delivery_address",
        "registered_by",
        "registered_by__user",
    ).order_by("-created_at")

    employee = None
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
        parcels_qs = parcels_qs.filter(registered_by=employee)

    data = [
        {
            "tracking_number": p.tracking_number,
            "status": p.current_status.name if p.current_status else "-",
            "delivery_type": p.get_delivery_type_display(),
            "price": float(p.price),
            "weight_kg": float(p.weight_kg),
            "sender": f"{p.sender.first_name} {p.sender.last_name}" if p.sender else "-",
            "receiver": f"{p.receiver.first_name} {p.receiver.last_name}" if p.receiver else "-",
            "sender_office": str(p.sender_office) if p.sender_office else "-",
            "receiver_office": str(p.receiver_office) if p.receiver_office else "-",
            "pickup_address": str(p.pickup_address) if p.pickup_address else "-",
            "delivery_address": str(p.delivery_address) if p.delivery_address else "-",
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": p.delivered_at.strftime("%Y-%m-%d %H:%M") if p.delivered_at else "-",
            "registered_by": str(p.registered_by) if p.registered_by else "-",
        }
        for p in parcels_qs
    ]

    return JsonResponse({
        "employee_id": employee.pk if employee else None,
        "employee_name": str(employee) if employee else "All Employees",
        "parcels_count": len(data),
        "parcels": data,
    })


@login_required
@employee_or_admin_required
def pending_deliveries_report(request):
    """Return all parcels that have been sent but not yet delivered."""
    terminal_codes = ["DELIVERED", "CANCELLED", "RETURNED"]

    parcels_qs = Parcel.objects.select_related(
        "sender",
        "receiver",
        "current_status",
        "sender_office",
        "receiver_office",
        "pickup_address",
        "delivery_address",
    ).exclude(
        current_status__code__in=terminal_codes
    ).order_by("-created_at")

    data = [
        {
            "tracking_number": p.tracking_number,
            "status": p.current_status.name if p.current_status else "-",
            "delivery_type": p.get_delivery_type_display(),
            "price": float(p.price),
            "weight_kg": float(p.weight_kg),
            "sender": f"{p.sender.first_name} {p.sender.last_name}" if p.sender else "-",
            "receiver": f"{p.receiver.first_name} {p.receiver.last_name}" if p.receiver else "-",
            "sender_office": str(p.sender_office) if p.sender_office else "-",
            "receiver_office": str(p.receiver_office) if p.receiver_office else "-",
            "pickup_address": str(p.pickup_address) if p.pickup_address else "-",
            "delivery_address": str(p.delivery_address) if p.delivery_address else "-",
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for p in parcels_qs
    ]

    return JsonResponse({
        "pending_count": len(data),
        "parcels": data,
    })


@login_required
@employee_or_admin_required
def income_report(request):
    """Return company income for a specified period."""

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    parcels_qs = Parcel.objects.select_related("current_status").filter(
        current_status__code="DELIVERED"
    )

    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d")
            parcels_qs = parcels_qs.filter(delivered_at__gte=date_from_parsed)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d")
            parcels_qs = parcels_qs.filter(delivered_at__lte=date_to_parsed)
        except ValueError:
            pass

    total_income = parcels_qs.aggregate(
        total=Sum(F("weight_kg") * F("tariff__price_per_kg"))
    )["total"] or 0
    parcels_count = parcels_qs.count()

    data = [
        {
            "tracking_number": p.tracking_number,
            "price": float(p.price),
            "delivery_type": p.get_delivery_type_display(),
            "delivered_at": p.delivered_at.strftime("%Y-%m-%d %H:%M") if p.delivered_at else "-",
            "sender": f"{p.sender.first_name} {p.sender.last_name}" if p.sender else "-",
            "receiver": f"{p.receiver.first_name} {p.receiver.last_name}" if p.receiver else "-",
        }
        for p in parcels_qs.select_related("sender", "receiver").order_by("-delivered_at")
    ]

    return JsonResponse({
        "date_from": date_from or "All time",
        "date_to": date_to or "All time",
        "total_income": float(total_income),
        "parcels_count": parcels_count,
        "parcels": data,
    })


@require_GET
def track_parcel_api(request):
    """Public API endpoint to track a parcel by tracking number."""
    tracking_number = request.GET.get("tracking_number", "").strip()

    if not tracking_number:
        return JsonResponse({"success": False, "error": "Tracking number is required."}, status=400)

    try:
        parcel = Parcel.objects.select_related(
            "current_status",
            "sender_office",
            "receiver_office",
            "pickup_address",
            "delivery_address",
        ).get(tracking_number__iexact=tracking_number)
    except Parcel.DoesNotExist:
        return JsonResponse({"success": False, "error": "Parcel not found."}, status=404)

    history = ParcelStatusHistory.objects.filter(parcel=parcel).select_related(
        "status", "office"
    ).order_by("-created_at")

    history_data = [
        {
            "status": h.status.name if h.status else "-",
            "status_code": h.status.code if h.status else "-",
            "office": str(h.office) if h.office else "-",
            "note": h.note or "",
            "timestamp": h.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for h in history
    ]

    return JsonResponse({
        "success": True,
        "parcel": {
            "tracking_number": parcel.tracking_number,
            "status": parcel.current_status.name if parcel.current_status else "-",
            "status_code": parcel.current_status.code if parcel.current_status else "-",
            "is_delivered": parcel.current_status.is_terminal if parcel.current_status else False,
            "delivery_type": parcel.get_delivery_type_display(),
            "weight_kg": float(parcel.weight_kg),
            "sender_office": str(parcel.sender_office) if parcel.sender_office else None,
            "receiver_office": str(parcel.receiver_office) if parcel.receiver_office else None,
            "pickup_address": str(parcel.pickup_address) if parcel.pickup_address else None,
            "delivery_address": str(parcel.delivery_address) if parcel.delivery_address else None,
            "created_at": parcel.created_at.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": parcel.delivered_at.strftime("%Y-%m-%d %H:%M") if parcel.delivered_at else None,
        },
        "history": history_data,
    })


# =============================================================================
# PARCELS CRUD API
# =============================================================================

def generate_tracking_number():
    """Generate a unique tracking number."""
    now = timezone.now()
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"EXP{now.strftime('%Y%m%d')}{unique_part}"


@login_required
@require_http_methods(["GET"])
def parcels_api_list(request):
    """API to list parcels and metadata for forms."""
    user = request.user
    is_employee = user.is_superuser or user.role in ("ADMIN", "EMPLOYEE")

    if is_employee:
        parcels_qs = Parcel.objects.all()
    else:
        parcels_qs = Parcel.objects.filter(Q(sender=user) | Q(receiver=user))

    parcels_qs = parcels_qs.select_related(
        "company", "sender", "receiver", "current_status",
        "sender_office", "receiver_office", "tariff"
    ).order_by("-created_at")

    parcels_data = [
        {
            "id": p.pk,
            "tracking_number": p.tracking_number,
            "sender_id": p.sender_id,
            "sender_name": f"{p.sender.first_name} {p.sender.last_name}" if p.sender else "-",
            "receiver_id": p.receiver_id,
            "receiver_name": f"{p.receiver.first_name} {p.receiver.last_name}" if p.receiver else "-",
            "sender_office_id": p.sender_office_id,
            "sender_office_name": str(p.sender_office) if p.sender_office else "",
            "receiver_office_id": p.receiver_office_id,
            "receiver_office_name": str(p.receiver_office) if p.receiver_office else "",
            "delivery_type": p.delivery_type,
            "weight_kg": float(p.weight_kg),
            "price": float(p.price),
            "status_code": p.current_status.code if p.current_status else "",
            "status_name": p.current_status.name if p.current_status else "",
            "is_terminal": p.current_status.is_terminal if p.current_status else False,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for p in parcels_qs
    ]

    # Get metadata for dropdowns (only for employees)
    metadata = {}
    if is_employee:
        # Clients (users with CLIENT role)
        clients = User.objects.filter(role=UserRole.CLIENT).order_by("first_name", "last_name")
        metadata["clients"] = [
            {"id": c.pk, "name": f"{c.first_name} {c.last_name}", "email": c.email}
            for c in clients
        ]

        # Offices
        offices = Office.objects.select_related("company").order_by("name")
        metadata["offices"] = [
            {"id": o.pk, "name": o.name, "code": o.code, "company": o.company.name}
            for o in offices
        ]

        # Statuses
        statuses = ParcelStatus.objects.all().order_by("code")
        metadata["statuses"] = [
            {"code": s.code, "name": s.name, "is_terminal": s.is_terminal}
            for s in statuses
        ]

        # Delivery types
        metadata["delivery_types"] = [
            {"value": dt.value, "label": dt.label}
            for dt in DeliveryType
        ]

        # Companies (for tariff selection)
        companies = Company.objects.all().order_by("name")
        metadata["companies"] = [{"id": c.pk, "name": c.name} for c in companies]

    return JsonResponse({
        "success": True,
        "parcels": parcels_data,
        "is_employee": is_employee,
        **metadata
    })


@login_required
@employee_or_admin_required
@require_http_methods(["POST"])
def parcels_api_create(request):
    """API to create a new parcel."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    # Validate required fields
    required = ["sender_id", "receiver_id", "weight_kg", "delivery_type"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}, status=400)

    # Validate sender and receiver
    try:
        sender = User.objects.get(pk=data["sender_id"])
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Sender not found."}, status=400)

    try:
        receiver = User.objects.get(pk=data["receiver_id"])
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Receiver not found."}, status=400)

    if sender.pk == receiver.pk:
        return JsonResponse({"success": False, "error": "Sender and receiver cannot be the same."}, status=400)

    # Validate weight
    try:
        weight_kg = Decimal(str(data["weight_kg"]))
        if weight_kg <= 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        return JsonResponse({"success": False, "error": "Invalid weight."}, status=400)

    # Validate delivery type
    if data["delivery_type"] not in [dt.value for dt in DeliveryType]:
        return JsonResponse({"success": False, "error": "Invalid delivery type."}, status=400)

    # Validate offices (at least one of sender_office or receiver_office required)
    sender_office = None
    receiver_office = None

    if data.get("sender_office_id"):
        try:
            sender_office = Office.objects.get(pk=data["sender_office_id"])
        except Office.DoesNotExist:
            return JsonResponse({"success": False, "error": "Sender office not found."}, status=400)

    if data.get("receiver_office_id"):
        try:
            receiver_office = Office.objects.get(pk=data["receiver_office_id"])
        except Office.DoesNotExist:
            return JsonResponse({"success": False, "error": "Receiver office not found."}, status=400)

    if not sender_office and not sender.default_address:
        return JsonResponse({"success": False, "error": "Sender office or sender's default address required."}, status=400)

    if not receiver_office and not receiver.default_address:
        return JsonResponse({"success": False, "error": "Receiver office or receiver's default address required."}, status=400)

    # Get company (from office or first company)
    company = None
    if sender_office:
        company = sender_office.company
    elif receiver_office:
        company = receiver_office.company
    else:
        company = Company.objects.first()

    # Get tariff
    tariff = None
    if company:
        tariff = Tariff.objects.filter(company=company, delivery_type=data["delivery_type"]).first()

    # Get CREATED status
    created_status = ParcelStatus.objects.filter(code="CREATED").first()
    if not created_status:
        return JsonResponse({"success": False, "error": "CREATED status not found. Run seed_data."}, status=500)

    # Get employee profile if exists
    employee = None
    if hasattr(request.user, "employee_profile"):
        employee = request.user.employee_profile

    try:
        with transaction.atomic():
            parcel = Parcel(
                tracking_number=generate_tracking_number(),
                company=company,
                sender=sender,
                receiver=receiver,
                sender_office=sender_office,
                receiver_office=receiver_office,
                pickup_address=sender.default_address if not sender_office else None,
                delivery_address=receiver.default_address if not receiver_office else None,
                delivery_type=data["delivery_type"],
                weight_kg=weight_kg,
                tariff=tariff,
                current_status=created_status,
                registered_by=employee,
            )
            parcel.save()

            # Create initial status history
            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=created_status,
                office=sender_office,
                changed_by=employee,
                note="Parcel registered",
            )

        return JsonResponse({
            "success": True,
            "parcel": {
                "id": parcel.pk,
                "tracking_number": parcel.tracking_number,
                "price": float(parcel.price),
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def parcels_api_get(request, parcel_id):
    """API to get a single parcel's details."""
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    # Check permission
    user = request.user
    is_employee = user.is_superuser or user.role in ("ADMIN", "EMPLOYEE")
    if not is_employee and parcel.sender_id != user.pk and parcel.receiver_id != user.pk:
        return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

    return JsonResponse({
        "success": True,
        "parcel": {
            "id": parcel.pk,
            "tracking_number": parcel.tracking_number,
            "company_id": parcel.company_id,
            "sender_id": parcel.sender_id,
            "receiver_id": parcel.receiver_id,
            "sender_office_id": parcel.sender_office_id,
            "receiver_office_id": parcel.receiver_office_id,
            "delivery_type": parcel.delivery_type,
            "weight_kg": float(parcel.weight_kg),
            "tariff_id": parcel.tariff_id,
            "price": float(parcel.price),
            "current_status_code": parcel.current_status.code if parcel.current_status else "",
            "current_status_name": parcel.current_status.name if parcel.current_status else "",
            "is_terminal": parcel.current_status.is_terminal if parcel.current_status else False,
            "created_at": parcel.created_at.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": parcel.delivered_at.strftime("%Y-%m-%d %H:%M") if parcel.delivered_at else None,
        }
    })


@login_required
@employee_or_admin_required
@require_http_methods(["PUT", "PATCH"])
def parcels_api_update(request, parcel_id):
    """API to update a parcel."""
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    # Can't update terminal parcels
    if parcel.current_status and parcel.current_status.is_terminal:
        return JsonResponse({"success": False, "error": "Cannot update a parcel with terminal status."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    try:
        with transaction.atomic():
            if "sender_id" in data:
                try:
                    parcel.sender = User.objects.get(pk=data["sender_id"])
                except User.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Sender not found."}, status=400)

            if "receiver_id" in data:
                try:
                    parcel.receiver = User.objects.get(pk=data["receiver_id"])
                except User.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Receiver not found."}, status=400)

            if "sender_office_id" in data:
                if data["sender_office_id"]:
                    try:
                        parcel.sender_office = Office.objects.get(pk=data["sender_office_id"])
                        parcel.pickup_address = None
                    except Office.DoesNotExist:
                        return JsonResponse({"success": False, "error": "Sender office not found."}, status=400)
                else:
                    parcel.sender_office = None
                    parcel.pickup_address = parcel.sender.default_address

            if "receiver_office_id" in data:
                if data["receiver_office_id"]:
                    try:
                        parcel.receiver_office = Office.objects.get(pk=data["receiver_office_id"])
                        parcel.delivery_address = None
                    except Office.DoesNotExist:
                        return JsonResponse({"success": False, "error": "Receiver office not found."}, status=400)
                else:
                    parcel.receiver_office = None
                    parcel.delivery_address = parcel.receiver.default_address

            if "weight_kg" in data:
                try:
                    parcel.weight_kg = Decimal(str(data["weight_kg"]))
                except (InvalidOperation, ValueError):
                    return JsonResponse({"success": False, "error": "Invalid weight."}, status=400)

            if "delivery_type" in data:
                if data["delivery_type"] not in [dt.value for dt in DeliveryType]:
                    return JsonResponse({"success": False, "error": "Invalid delivery type."}, status=400)
                parcel.delivery_type = data["delivery_type"]
                # Update tariff to match new delivery type
                if parcel.company:
                    parcel.tariff = Tariff.objects.filter(
                        company=parcel.company, delivery_type=data["delivery_type"]
                    ).first()

            parcel.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@employee_or_admin_required
@require_http_methods(["DELETE"])
def parcels_api_delete(request, parcel_id):
    """API to delete a parcel."""
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    # Only allow deleting CREATED or CANCELLED parcels
    if parcel.current_status and parcel.current_status.code not in ("CREATED", "CANCELLED"):
        return JsonResponse({
            "success": False,
            "error": "Can only delete parcels with CREATED or CANCELLED status."
        }, status=400)

    try:
        parcel.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@employee_or_admin_required
@require_http_methods(["POST"])
def parcels_api_update_status(request, parcel_id):
    """API to update a parcel's status."""
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    if parcel.current_status and parcel.current_status.is_terminal:
        return JsonResponse({"success": False, "error": "Parcel already has terminal status."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    status_code = data.get("status_code")
    if not status_code:
        return JsonResponse({"success": False, "error": "status_code is required."}, status=400)

    try:
        new_status = ParcelStatus.objects.get(code=status_code)
    except ParcelStatus.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid status code."}, status=400)

    # Get employee profile if exists
    employee = None
    if hasattr(request.user, "employee_profile"):
        employee = request.user.employee_profile

    # Get office from data or employee's office
    office = None
    if data.get("office_id"):
        try:
            office = Office.objects.get(pk=data["office_id"])
        except Office.DoesNotExist:
            pass
    elif employee and employee.office:
        office = employee.office

    try:
        with transaction.atomic():
            parcel.current_status = new_status

            # Set delivered_at if status is DELIVERED
            if new_status.code == "DELIVERED":
                parcel.delivered_at = timezone.now()

            parcel.save()

            # Create status history entry
            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=new_status,
                office=office,
                changed_by=employee,
                note=data.get("note", ""),
            )

        return JsonResponse({
            "success": True,
            "status": {
                "code": new_status.code,
                "name": new_status.name,
                "is_terminal": new_status.is_terminal,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
