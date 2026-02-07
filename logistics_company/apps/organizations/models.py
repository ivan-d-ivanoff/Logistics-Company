from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)
    bulstat = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.ForeignKey("common.Address", on_delete=models.PROTECT, related_name="companies")

    def __str__(self):
        return self.name


class Office(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="offices")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.ForeignKey("common.Address", on_delete=models.PROTECT, related_name="offices")
    working_hours = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"