from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from .models import Parcel

def parcels(request):
    return render(request, "parcels/parcels.html")


class ParcelForm(ModelForm):
    class Meta:
        model = Parcel
        fields = "__all__"


def parcel_list(request):
    parcels = Parcel.objects.select_related("status")
    return render(
        request,
        "parcel_list.html",
        {
            "parcels": parcels
        }
    )


def parcel_create(request):
    if request.method == "POST":
        form = ParcelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("parcel_list")
    else:
        form = ParcelForm()

    return render(
        request,
        "parcel_form.html",
        {
            "form": form
        }
    )


def parcel_update(request, pk):
    parcel = get_object_or_404(Parcel, pk=pk)

    if request.method == "POST":
        form = ParcelForm(request.POST, instance=parcel)
        if form.is_valid():
            form.save()
            return redirect("parcel_list")
    else:
        form = ParcelForm(instance=parcel)

    return render(
        request,
        "parcel_form.html",
        {
            "form": form,
            "parcel": parcel,
        }
    )


def parcel_delete(request, pk):
    parcel = get_object_or_404(Parcel, pk=pk)

    if request.method == "POST":
        parcel.delete()
        return redirect("parcel_list")

    return render(
        request,
        "parcel_confirm_delete.html",
        {
            "parcel": parcel
        }
    )
