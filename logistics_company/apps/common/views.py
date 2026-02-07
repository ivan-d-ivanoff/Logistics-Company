from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from apps.accounts.models import User, UserRole
from apps.workforce.models import Employee


def employee_or_admin_required(view_func):
    """Decorator that requires user to be an employee, admin, or superuser."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_superuser or request.user.role in ("ADMIN", "EMPLOYEE"):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view


@login_required
def dashboard(request):
    """Redirect to appropriate page based on role."""
    if request.user.role == "CLIENT":
        return redirect("client_dashboard")
    return redirect("parcels")


@login_required
@employee_or_admin_required
def reports(request):
    clients = User.objects.filter(role=UserRole.CLIENT).order_by("first_name", "last_name")
    employees = Employee.objects.select_related("user").order_by("user__first_name", "user__last_name")

    return render(request, "reports.html", {
        "clients": clients,
        "employees": employees,
    })


def index(request):
    return render(request, "index.html")


def track(request):
    return render(request, "parcels/track.html")
