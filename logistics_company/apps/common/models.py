from django.db import models


class Address(models.Model):
    country = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    postal_code = models.CharField(max_length=45)
    street = models.CharField(max_length=45)
    details = models.CharField(max_length=45, blank=True)

    def __str__(self) -> str:
        return f"{self.country}, {self.city}, {self.postal_code}, {self.street}"
