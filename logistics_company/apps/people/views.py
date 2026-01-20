from django.shortcuts import render, get_object_or_404, redirect
from django.forms import ModelForm

from .models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = "__all__"


def client_list(request):
    clients = Client.objects.select_related(
        "default_address",
        "prefered_address",
    )
    return render(
        request,
        "clients_list.html",
        {
            "clients": clients
        }
    )


def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm()

    return render(
        request,
        "clients_form.html",
        {
            "form": form
        }
    )


def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)

    return render(
        request,
        "clients_form.html",
        {
            "form": form,
            "client": client,
        }
    )


def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        client.delete()
        return redirect("client_list")

    return render(
        request,
        "client_confirm_delete.html",
        {
            "client": client
        }
    )
