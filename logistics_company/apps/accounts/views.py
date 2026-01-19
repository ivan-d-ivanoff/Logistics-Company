from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect

User = get_user_model()

from .forms import RegisterForm
from apps.people.models import Client


def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user_obj = None

        if user_obj:
            auth_user = authenticate(request, username=user_obj.username, password=password)
        else:
            auth_user = None

        if auth_user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/accounts.html")

        login(request, auth_user)

        if auth_user.is_superuser or auth_user.role == "ADMIN":
            return redirect("/admin/")
        if auth_user.role == "EMPLOYEE":
            return redirect("employee_dashboard")
        return redirect("client_dashboard")

    return render(request, "accounts/accounts.html")


def register_view(request):
    # ако вече е логнат – връщаме го към login (или друга страница)
    if request.user.is_authenticated:
        if request.user.role == "EMPLOYEE" or request.user.is_superuser:
            return redirect("employee_dashboard")
        return redirect("client_dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # автоматично създаваме Client профил
            Client.objects.create(user=user)

            # логваме потребителя
            login(request, user)

            # временно го пращаме към login или друга сигурна страница
            return redirect("/accounts/login/")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")

def client_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.role != "CLIENT":
        return redirect("employee_dashboard")
    return render(request, "accounts/client_dashboard.html")


def employee_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.role != "EMPLOYEE" and not request.user.is_superuser:
        return redirect("client_dashboard")
    return render(request, "employees/employees.html")


