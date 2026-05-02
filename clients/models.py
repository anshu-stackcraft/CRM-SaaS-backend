from django.db import models
from decimal import Decimal
from django.conf import settings

class Client(models.Model):
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=17, unique=True)
    phone = models.CharField(max_length=15)
    country = models.CharField(max_length=255, default='India')
    comments = models.TextField(blank=True)
    follow_up_time = models.DateTimeField(null=True, blank=True)
    payment = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    ACTION_CHOICES = (
        ('call', 'Call'),
        ('follow_up', 'Follow Up'),
        ('closed', 'Closed'),
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClientImportFile(models.Model):
    file = models.FileField(upload_to="imports/clients/")
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_import_files",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
    total_rows = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_name} ({self.created_at:%Y-%m-%d %H:%M})"
