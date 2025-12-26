from django.db import models


class Employee(models.Model):
    class EmployeeType(models.TextChoices):
        COURIER = "COURIER", "Courier"
        OFFICE = "OFFICE", "Office staff"
        MANAGER = "MANAGER", "Manager"

    user = models.OneToOneField(
        "accounts.AppUser",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="employee_profile",
    )

    employee_type = models.CharField(max_length=20, choices=EmployeeType.choices)
    office = models.ForeignKey(
        "organizations.Office",
        on_delete=models.PROTECT,
        related_name="employees",
    )
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.employee_type})"
