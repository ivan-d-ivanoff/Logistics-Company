from django.shortcuts import render

from django.http import JsonResponse

from .models import Client


def clients(request):
    return render(request, "people/clients.html")

def clients_report(request):
    clients = Client.objects.select_related(
        "default_address",
        "prefered_address"
    ).all()

    data = [
        {
            "id": client.id,
            "default_address": str(client.default_address) if client.default_address else None,
            "prefered_address": str(client.prefered_address) if client.prefered_address else None,
        }
        for client in clients
    ]

    return JsonResponse(
        {"clients_report": data},
        safe=False,
    )