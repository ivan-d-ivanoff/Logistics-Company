from django.db import models


class Client(models.Model):
    default_address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="default_for_clients",
        null=True,
        blank=True,
    )
    prefered_address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="preferred_for_clients",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"Client #{self.pk}"
