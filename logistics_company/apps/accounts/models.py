from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    EMPLOYEE = "EMPLOYEE", "Employee"
    CLIENT = "CLIENT", "Client"


class User(AbstractUser):
    """
    Custom user model for the project.
    Uses Django auth system, supports admin panel, permissions, login/logout etc.
    """

    # Make email unique (we can also use it for login later if you want)
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=45, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
