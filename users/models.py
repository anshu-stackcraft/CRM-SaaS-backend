from django.contrib.auth.models import AbstractUser
from django.conf import settings
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
    theme_preference = models.CharField(
        max_length=10,
        choices=(("light", "Light"), ("dark", "Dark")),
        default="light",
    )

    # 🔥 Display name
    def __str__(self):
        return self.full_name if self.full_name else self.username

    # 🔥 Save override (auto full_name fallback)
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)


class Attendance(models.Model):
    STATUS_CHOICES = (
        ("present", "Present"),
        ("absent", "Absent"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    employee_id = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    source = models.CharField(max_length=50, default="scan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} attendance {self.created_at:%Y-%m-%d %H:%M}"
