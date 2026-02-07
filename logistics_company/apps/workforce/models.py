from django.db import models
from django.core.validators import MinValueValidator


class Employee(models.Model):
    class EmployeeType(models.TextChoices):
        COURIER = "COURIER", "Courier"
        OFFICE = "OFFICE", "Office"
        MANAGER = "MANAGER", "Manager"

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, primary_key=True, related_name="employee_profile")
    employee_code = models.CharField(max_length=20, unique=True)
    employee_type = models.CharField(max_length=20, choices=EmployeeType.choices)
    office = models.ForeignKey("organizations.Office", on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_code})"