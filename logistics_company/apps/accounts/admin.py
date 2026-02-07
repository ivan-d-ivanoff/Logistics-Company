from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserAddress
from .forms_admin import CustomUserCreationForm


class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 0
    fields = ("address", "label", "is_default")
    raw_id_fields = ("address",)


@admin.register(User)
class AppUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    list_display = ("username", "email", "full_name", "role", "phone", "is_staff", "is_superuser", "created_at")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "created_at")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    date_hierarchy = "created_at"

    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {"fields": ("role", "phone", "default_address", "preferred_address", "created_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "first_name", "last_name", "phone", "password1", "password2"),
        }),
    )

    readonly_fields = ("created_at",)
    raw_id_fields = ("default_address", "preferred_address")

    inlines = [UserAddressInline]

    @admin.display(description="Full Name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "-"


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "label", "is_default")
    list_filter = ("is_default",)
    search_fields = ("user__username", "user__email", "label", "address__city", "address__street")
    raw_id_fields = ("user", "address")
