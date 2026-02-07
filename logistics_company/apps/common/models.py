from django.db import models
from django.core.validators import MinValueValidator


class DeliveryType(models.TextChoices):
    STANDARD = "STANDARD", "Standard"
    EXPRESS = "EXPRESS", "Express"


class Address(models.Model):
    country = models.CharField(max_length=60)
    city = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=20)
    street = models.CharField(max_length=120)
    details = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"


class Tariff(models.Model):
    company = models.ForeignKey(
        "organizations.Company", on_delete=models.CASCADE, related_name="tariffs"
    )
    delivery_type = models.CharField(
        max_length=20, choices=DeliveryType.choices, default=DeliveryType.STANDARD
    )
    price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "delivery_type"], name="uniq_comp_del_addr")
        ]

    def __str__(self):
        return f"{self.company.name} - {self.get_delivery_type_display()} ({self.price_per_kg}/kg)"