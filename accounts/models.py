from django.contrib.auth.models import AbstractUser
from django.db import models


class Business(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        STAFF = "staff", "Staff"

    email = models.EmailField(unique=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="members",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)

    def __str__(self):
        return self.username