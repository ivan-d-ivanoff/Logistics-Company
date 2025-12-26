from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=45)
    bulstat = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="companies",
    )

    def __str__(self) -> str:
        return self.name


class Office(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="offices",
    )
    name = models.CharField(max_length=45)
    phone = models.CharField(max_length=20)
    address = models.ForeignKey(
        "common.Address",
        on_delete=models.PROTECT,
        related_name="offices",
    )
    working_hours = models.CharField(max_length=45)

    def __str__(self) -> str:
        return f"{self.company.name} - {self.name}"
