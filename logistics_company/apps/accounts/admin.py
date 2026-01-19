from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .forms_admin import CustomUserCreationForm


@admin.register(User)
class AppUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {"fields": ("role", "phone", "created_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "first_name", "last_name", "phone", "password1", "password2"),
        }),
    )

    readonly_fields = ("created_at",)
