
from django.shortcuts import render

def parcels(request):
    return render(request, "parcels/parcels.html")
