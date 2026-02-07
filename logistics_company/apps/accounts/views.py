from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

User = get_user_model()

from .forms import RegisterForm, ProfileForm, CustomPasswordChangeForm
from apps.parcels.models import Parcel


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
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": "Incorrect credentials"})
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/accounts.html")

        login(request, auth_user)

        if auth_user.is_superuser or auth_user.role == "ADMIN":
            redirect_url = "/admin/"
        elif auth_user.role == "EMPLOYEE":
            redirect_url = reverse("parcels")
        else:
            redirect_url = reverse("client_dashboard")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "redirect": redirect_url})

        return redirect(redirect_url)

    return render(request, "accounts/accounts.html")


def register_view(request):
    if request.user.is_authenticated:
        if request.user.role == "EMPLOYEE" or request.user.is_superuser:
            return redirect("parcels")
        return redirect("client_dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("client_dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def client_dashboard_view(request):
    if request.user.role != "CLIENT":
        return redirect("parcels")

    sent_parcels = Parcel.objects.filter(sender=request.user).select_related(
        "company", "receiver", "current_status", "sender_office", "receiver_office", "tariff"
    ).order_by("-created_at")

    received_parcels = Parcel.objects.filter(receiver=request.user).select_related(
        "company", "sender", "current_status", "sender_office", "receiver_office", "tariff"
    ).order_by("-created_at")

    return render(request, "accounts/client_dashboard.html", {
        "sent_parcels": sent_parcels,
        "received_parcels": received_parcels,
    })


@login_required
def employee_dashboard_view(request):
    """Redirect to parcels page - employee dashboard removed."""
    if request.user.role == "CLIENT":
        return redirect("client_dashboard")
    return redirect("parcels")


@login_required
def profile_view(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = CustomPasswordChangeForm(user=request.user)

    if request.method == "POST":
        if "update_profile" in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("profile")

        elif "change_password" in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")

    return render(request, "accounts/profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })


