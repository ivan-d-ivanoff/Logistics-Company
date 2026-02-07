from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    EMPLOYEE = "EMPLOYEE", "Employee"
    CLIENT = "CLIENT", "Client"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)

    default_address = models.ForeignKey(
        "common.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="default_for_users"
    )
    preferred_address = models.ForeignKey(
        "common.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="preferred_for_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address_links")
    address = models.ForeignKey("common.Address", on_delete=models.CASCADE, related_name="user_links")
    label = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "address"], name="uniq_user_address"),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.address}"