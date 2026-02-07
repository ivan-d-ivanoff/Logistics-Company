from django.contrib import admin
from django.utils.html import format_html

from .models import Parcel, ParcelStatus, ParcelStatusHistory, ParcelNote


class ParcelStatusHistoryInline(admin.TabularInline):
    model = ParcelStatusHistory
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("status", "office", "changed_by", "note", "created_at")
    ordering = ("-created_at",)


class ParcelNoteInline(admin.TabularInline):
    model = ParcelNote
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("note_type", "content", "created_by", "created_at")
    ordering = ("-created_at",)


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "sender_name",
        "receiver_name",
        "status_badge",
        "delivery_type",
        "weight_kg",
        "calculated_price",
        "created_at",
    )
    list_filter = (
        "current_status",
        "delivery_type",
        "company",
        "sender_office",
        "receiver_office",
        "created_at",
    )
    search_fields = (
        "tracking_number",
        "sender__username",
        "sender__email",
        "sender__first_name",
        "sender__last_name",
        "receiver__username",
        "receiver__email",
        "receiver__first_name",
        "receiver__last_name",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "calculated_price")
    raw_id_fields = ("sender", "receiver", "registered_by")

    fieldsets = (
        ("Tracking", {
            "fields": ("tracking_number", "company", "current_status")
        }),
        ("Sender & Receiver", {
            "fields": ("sender", "receiver")
        }),
        ("Locations", {
            "fields": ("sender_office", "receiver_office", "pickup_address", "delivery_address")
        }),
        ("Delivery Details", {
            "fields": ("delivery_type", "weight_kg", "tariff", "calculated_price")
        }),
        ("Staff & Dates", {
            "fields": ("registered_by", "created_at", "delivered_at")
        }),
    )

    inlines = [ParcelStatusHistoryInline, ParcelNoteInline]

    @admin.display(description="Sender")
    def sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}"
        return "-"

    @admin.display(description="Receiver")
    def receiver_name(self, obj):
        if obj.receiver:
            return f"{obj.receiver.first_name} {obj.receiver.last_name}"
        return "-"

    @admin.display(description="Status")
    def status_badge(self, obj):
        if not obj.current_status:
            return "-"
        colors = {
            "CREATED": "#6c757d",
            "IN_TRANSIT": "#17a2b8",
            "OUT_FOR_DELIVERY": "#ffc107",
            "DELIVERED": "#28a745",
            "RETURNED": "#dc3545",
            "CANCELLED": "#343a40",
        }
        color = colors.get(obj.current_status.code, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.current_status.name
        )

    @admin.display(description="Price")
    def calculated_price(self, obj):
        return f"{obj.price:.2f} BGN"


@admin.register(ParcelStatus)
class ParcelStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description", "is_terminal")
    list_filter = ("is_terminal",)
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(ParcelStatusHistory)
class ParcelStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("parcel", "status", "office", "changed_by", "note", "created_at")
    list_filter = ("status", "office", "created_at")
    search_fields = ("parcel__tracking_number", "note")
    date_hierarchy = "created_at"
    raw_id_fields = ("parcel", "changed_by")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(ParcelNote)
class ParcelNoteAdmin(admin.ModelAdmin):
    list_display = ("parcel", "note_type", "short_content", "created_by", "created_at")
    list_filter = ("note_type", "created_at")
    search_fields = ("parcel__tracking_number", "content")
    date_hierarchy = "created_at"
    raw_id_fields = ("parcel", "created_by")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    @admin.display(description="Content")
    def short_content(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
