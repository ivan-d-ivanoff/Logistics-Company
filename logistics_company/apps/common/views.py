from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboards.html")

def reports(request):
    return render(request, "reports.html")

def index(request):
    return render(request, "index.html")

def track(request):
    return render(request, "track.html")
