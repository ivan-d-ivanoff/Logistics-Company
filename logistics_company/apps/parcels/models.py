from django.db import models


class ParcelStatus(models.Model):
    class StatusChoices(models.TextChoices):
        CREATED = "CREATED", "Created"
        IN_TRANSIT = "IN_TRANSIT", "In transit"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for delivery"
        DELIVERED = "DELIVERED", "Delivered"
        RETURNED = "RETURNED", "Returned"
        CANCELLED = "CANCELLED", "Cancelled"

    status = models.CharField(max_length=20, choices=StatusChoices.choices)
    description = models.CharField(max_length=45, blank=True)

    def __str__(self) -> str:
        return self.status


class Parcel(models.Model):
    class DeliveryType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        EXPRESS = "EXPRESS", "Express"

    tracking_number = models.CharField(max_length=45, unique=True)

    sender_client = models.ForeignKey(
        "people.Client",
        on_delete=models.PROTECT,
        related_name="sent_parcels",
    )
    receiver_client = models.ForeignKey(
        "people.Client",
        on_delete=models.PROTECT,
        related_name="received_parcels",
    )

    sender_office = models.ForeignKey(
        "organizations.Office",
        on_delete=models.PROTECT,
        related_name="sent_parcels",
        null=True,
        blank=True,
    )
    receiver_office = models.ForeignKey(
        "organizations.Office",
        on_delete=models.PROTECT,
        related_name="received_parcels",
        null=True,
        blank=True,
    )

    pickup_address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="pickup_parcels",
    )
    delivery_address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="delivery_parcels",
    )

    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices)
    status = models.ForeignKey(
        ParcelStatus,
        on_delete=models.PROTECT,
        related_name="parcels",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    registered_by_employee = models.ForeignKey(
        "workforce.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registered_parcels",
    )

    def __str__(self) -> str:
        return self.tracking_number
