from django.shortcuts import render

def offices(request):
    return render(request, "organizations/offices.html")
