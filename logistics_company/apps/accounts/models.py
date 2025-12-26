from django.db import models


class Role(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EMPLOYEE = "EMPLOYEE", "Employee"
        CLIENT = "CLIENT", "Client"

    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    description = models.CharField(max_length=45, blank=True)

    def __str__(self) -> str:
        return self.role


class AppUser(models.Model):
    username = models.CharField(max_length=45, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    phone = models.CharField(max_length=45, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
    )

    def __str__(self) -> str:
        return self.username
