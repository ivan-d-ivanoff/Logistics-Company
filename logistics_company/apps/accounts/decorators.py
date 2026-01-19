from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def employee_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_superuser or request.user.role in ("ADMIN", "EMPLOYEE"):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Employees only.")
    return _wrapped


def client_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role == "CLIENT":
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Clients only.")
    return _wrapped
