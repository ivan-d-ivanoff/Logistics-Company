from django.contrib import admin

from .models import Address, Tariff


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("city", "street", "postal_code", "country", "details")
    list_filter = ("country", "city")
    search_fields = ("city", "street", "postal_code", "details")
    ordering = ("country", "city", "street")

    fieldsets = (
        (None, {
            "fields": ("country", "city", "postal_code")
        }),
        ("Street Address", {
            "fields": ("street", "details")
        }),
    )


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("company", "delivery_type", "price_per_kg_display")
    list_filter = ("company", "delivery_type")
    search_fields = ("company__name",)
    ordering = ("company", "delivery_type")

    @admin.display(description="Price per kg")
    def price_per_kg_display(self, obj):
        return f"{obj.price_per_kg:.2f} BGN"
