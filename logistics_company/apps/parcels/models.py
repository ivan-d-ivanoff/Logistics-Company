from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator

from apps.common.models import DeliveryType


class ParcelStatus(models.Model):
    """
    Parcel status stored in database. Predefined statuses should be seeded.
    Standard codes: CREATED, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, RETURNED, CANCELLED
    """
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=50, default="")
    description = models.CharField(max_length=255, blank=True)
    is_terminal = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Parcel statuses"

    def __str__(self):
        return self.name


class Parcel(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True, db_index=True)

    company = models.ForeignKey(
        "organizations.Company", on_delete=models.PROTECT, related_name="parcels",
        null=True, blank=True  # Nullable for migration; should be set when creating parcels
    )

    sender = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="sent_parcels"
    )
    receiver = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="received_parcels"
    )

    sender_office = models.ForeignKey(
        "organizations.Office", on_delete=models.SET_NULL, null=True, blank=True, related_name="outgoing_parcels"
    )
    receiver_office = models.ForeignKey(
        "organizations.Office", on_delete=models.SET_NULL, null=True, blank=True, related_name="incoming_parcels"
    )
    pickup_address = models.ForeignKey(
        "common.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="pickup_parcels"
    )
    delivery_address = models.ForeignKey(
        "common.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="delivery_parcels"
    )

    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices, default=DeliveryType.STANDARD)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(0.001)])
    tariff = models.ForeignKey(
        "common.Tariff", on_delete=models.SET_NULL, null=True, blank=True, related_name="parcels"
    )

    current_status = models.ForeignKey(ParcelStatus, on_delete=models.PROTECT, related_name="parcels")

    registered_by = models.ForeignKey(
        "workforce.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="registered_parcels"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    @property
    def price(self):
        """Calculate price based on weight and tariff."""
        if self.tariff and self.weight_kg:
            return self.weight_kg * self.tariff.price_per_kg
        return Decimal("0.00")

    def clean(self):
        """Validate parcel has proper origin and destination."""
        errors = {}

        has_sender_office = self.sender_office_id is not None
        has_pickup_address = self.pickup_address_id is not None

        if not has_sender_office and not has_pickup_address:
            errors["sender_office"] = "Parcel must have either a sender office or a pickup address."

        has_receiver_office = self.receiver_office_id is not None
        has_delivery_address = self.delivery_address_id is not None

        if not has_receiver_office and not has_delivery_address:
            errors["receiver_office"] = "Parcel must have either a receiver office or a delivery address."

        if self.tariff_id and self.tariff and self.tariff.delivery_type != self.delivery_type:
            errors["tariff"] = f"Tariff delivery type ({self.tariff.delivery_type}) must match parcel delivery type ({self.delivery_type})."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_number


class ParcelStatusHistory(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="status_history")
    status = models.ForeignKey(ParcelStatus, on_delete=models.PROTECT, related_name="history_entries")
    office = models.ForeignKey(
        "organizations.Office", on_delete=models.SET_NULL, null=True, blank=True, related_name="status_events"
    )
    changed_by = models.ForeignKey(
        "workforce.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="status_changes"
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Parcel status histories"
        indexes = [
            models.Index(fields=["parcel", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.parcel.tracking_number} -> {self.status.code}"


class ParcelNote(models.Model):
    class NoteType(models.TextChoices):
        GENERAL = "GENERAL", "General"
        DELIVERY = "DELIVERY", "Delivery"
        ISSUE = "ISSUE", "Issue"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="notes")
    note_type = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.GENERAL)
    content = models.TextField()
    created_by = models.ForeignKey(
        "workforce.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="parcel_notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.tracking_number} ({self.note_type})"
