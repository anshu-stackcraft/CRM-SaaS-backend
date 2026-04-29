from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('technical_admin', 'Technical Admin'),
        ('employee', 'Employee'),
    )

    # 🔐 Role
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee'
    )

    # 👤 Profile Fields
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    # 📧 Email (unique + required)
    email = models.EmailField(unique=True)

    # ⏱️ Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🔥 Display name
    def __str__(self):
        return self.full_name if self.full_name else self.username

    # 🔥 Save override (auto full_name fallback)
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)