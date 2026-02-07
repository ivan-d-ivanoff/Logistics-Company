import json
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.accounts.models import User, UserRole
from apps.common.models import Address


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
def clients(request):
    return render(request, "people/clients.html")


@login_required
@employee_or_admin_required
def clients_report(request):
    """Return all clients (users with CLIENT role) with their details."""
    clients = User.objects.filter(role=UserRole.CLIENT).order_by("first_name", "last_name")

    data = [
        {
            "id": client.id,
            "username": client.username,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone": client.phone or "-",
            "default_address": str(client.default_address) if client.default_address else "-",
            "created_at": client.created_at.strftime("%Y-%m-%d %H:%M") if client.created_at else "-",
        }
        for client in clients
    ]

    return JsonResponse({
        "clients_count": len(data),
        "clients": data,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Clients CRUD API
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@employee_or_admin_required
@require_http_methods(["GET"])
def clients_api_list(request):
    """List all clients."""
    clients = User.objects.filter(role=UserRole.CLIENT).order_by("first_name", "last_name")

    data = []
    for client in clients:
        data.append({
            "id": client.id,
            "username": client.username,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone": client.phone or "",
            "address_city": client.default_address.city if client.default_address else "",
            "address_street": client.default_address.street if client.default_address else "",
            "address_postal": client.default_address.postal_code if client.default_address else "",
            "created_at": client.created_at.strftime("%Y-%m-%d") if client.created_at else "",
        })

    return JsonResponse({"success": True, "clients": data})


@login_required
@employee_or_admin_required
@require_http_methods(["POST"])
def clients_api_create(request):
    """Create a new client."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    # Required fields
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip()

    if not first_name or not last_name:
        return JsonResponse({"success": False, "error": "First name and last name are required."}, status=400)
    if not email:
        return JsonResponse({"success": False, "error": "Email is required."}, status=400)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "error": "A user with this email already exists."}, status=400)

    # Generate username from email
    username = email.split("@")[0]
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    # Optional fields
    phone = data.get("phone", "").strip()
    password = data.get("password", "").strip() or "client123"

    # Create address if provided
    address = None
    addr_data = data.get("address", {})
    if addr_data.get("city") or addr_data.get("street"):
        address = Address.objects.create(
            city=addr_data.get("city", ""),
            street=addr_data.get("street", ""),
            postal_code=addr_data.get("postal_code", ""),
            country=addr_data.get("country", "Bulgaria"),
        )

    # Create client
    client = User.objects.create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=UserRole.CLIENT,
        default_address=address,
        password=make_password(password),
    )

    return JsonResponse({"success": True, "client_id": client.id})


@login_required
@employee_or_admin_required
@require_http_methods(["GET"])
def clients_api_get(request, client_id):
    """Get a single client."""
    try:
        client = User.objects.get(id=client_id, role=UserRole.CLIENT)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Client not found."}, status=404)

    data = {
        "id": client.id,
        "username": client.username,
        "first_name": client.first_name,
        "last_name": client.last_name,
        "email": client.email,
        "phone": client.phone or "",
        "address_city": client.default_address.city if client.default_address else "",
        "address_street": client.default_address.street if client.default_address else "",
        "address_postal": client.default_address.postal_code if client.default_address else "",
        "created_at": client.created_at.strftime("%Y-%m-%d") if client.created_at else "",
    }

    return JsonResponse({"success": True, "client": data})


@login_required
@employee_or_admin_required
@require_http_methods(["PUT"])
def clients_api_update(request, client_id):
    """Update a client."""
    try:
        client = User.objects.get(id=client_id, role=UserRole.CLIENT)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Client not found."}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    # Update fields
    if "first_name" in data:
        client.first_name = data["first_name"].strip()
    if "last_name" in data:
        client.last_name = data["last_name"].strip()
    if "email" in data:
        new_email = data["email"].strip()
        if new_email != client.email:
            if User.objects.filter(email=new_email).exclude(id=client.id).exists():
                return JsonResponse({"success": False, "error": "A user with this email already exists."}, status=400)
            client.email = new_email
    if "phone" in data:
        client.phone = data["phone"].strip()
    if "password" in data and data["password"].strip():
        client.password = make_password(data["password"].strip())

    # Update address
    addr_data = data.get("address", {})
    if addr_data:
        if client.default_address:
            client.default_address.city = addr_data.get("city", client.default_address.city)
            client.default_address.street = addr_data.get("street", client.default_address.street)
            client.default_address.postal_code = addr_data.get("postal_code", client.default_address.postal_code)
            client.default_address.save()
        else:
            address = Address.objects.create(
                city=addr_data.get("city", ""),
                street=addr_data.get("street", ""),
                postal_code=addr_data.get("postal_code", ""),
                country=addr_data.get("country", "Bulgaria"),
            )
            client.default_address = address

    client.save()
    return JsonResponse({"success": True})


@login_required
@employee_or_admin_required
@require_http_methods(["DELETE"])
def clients_api_delete(request, client_id):
    """Delete a client."""
    try:
        client = User.objects.get(id=client_id, role=UserRole.CLIENT)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Client not found."}, status=404)

    # Check for related parcels
    sent_count = client.sent_parcels.count()
    received_count = client.received_parcels.count()

    if sent_count > 0 or received_count > 0:
        return JsonResponse({
            "success": False,
            "error": f"Cannot delete client with existing parcels. This client has {sent_count} sent and {received_count} received parcels."
        }, status=400)

    # Store address to delete after user
    address = client.default_address

    client.delete()

    # Delete orphaned address
    if address:
        address.delete()

    return JsonResponse({"success": True})
