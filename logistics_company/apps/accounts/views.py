from django.shortcuts import render, redirect

def login_view(request):
    return render(request, "accounts/accounts.html")

def register_view(request):
    return render(request, "accounts/accounts.html")

def logout_view(request):
    return redirect("index")

