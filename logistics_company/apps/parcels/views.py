from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Parcel
from apps.people.models import Client



def client_parcels_report(request, client_id=None, role="all"):
    """
    role: 'sent' -> sender_client
          'received' -> receiver_client
          'all' -> all parcels
    """
    parcels = Parcel.objects.select_related(
        "sender_client",
        "receiver_client",
        "status",
        "sender_office",
        "receiver_office",
        "pickup_address",
        "delivery_address",
    ).order_by("-created_at")

    if role == "sent":
        if client_id is None:
            return JsonResponse({"error": "client_id is required for sent parcels"}, status=400)
        client = get_object_or_404(Client, pk=client_id)
        parcels = parcels.filter(sender_client=client)
    elif role == "received":
        if client_id is None:
            return JsonResponse({"error": "client_id is required for received parcels"}, status=400)
        client = get_object_or_404(Client, pk=client_id)
        parcels = parcels.filter(receiver_client=client)
    elif role == "all":
        client = None
    else:
        return JsonResponse({"error": "Invalid role"}, status=400)

    data = [
        {
            "tracking_number": p.tracking_number,
            "status": p.status.status,
            "delivery_type": p.delivery_type,
            "price": float(p.price),
            "weight_kg": float(p.weight_kg),
            "sender_client": str(p.sender_client),
            "receiver_client": str(p.receiver_client),
            "sender_office": str(p.sender_office) if p.sender_office else "-",
            "receiver_office": str(p.receiver_office) if p.receiver_office else "-",
            "pickup_address": str(p.pickup_address),
            "delivery_address": str(p.delivery_address),
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": p.delivered_at.strftime("%Y-%m-%d %H:%M") if p.delivered_at else "-",
        }
        for p in parcels
    ]

    return JsonResponse({
        "client_id": client.id if client else None,
        "parcels_count": parcels.count(),
        "parcels": data,
    })



@login_required
def parcels(request):
    user = request.user

    is_employee = user.is_superuser or user.role in ("ADMIN", "EMPLOYEE")
    can_register_parcel = is_employee  # само служители/админ

    if is_employee:
        parcels_qs = Parcel.objects.all()
    else:
        # CLIENT: вижда само пратките, които е изпратил или получил
        parcels_qs = Parcel.objects.filter(
            Q(sender_client__user=user) | Q(receiver_client__user=user)
        )

    # по желание: за по-малко заявки в template
    parcels_qs = parcels_qs.select_related(
        "sender_client",
        "receiver_client",
        "pickup_address",
        "delivery_address",
        "status",
        "registered_by_employee",
    ).order_by("-created_at")

    return render(
        request,
        "parcels/parcels.html",   # ако при теб е parcels/parcels.html -> смени тук
        {
            "parcels": parcels_qs,
            "can_register_parcel": can_register_parcel,
        },
    )
