from django.db import models
from django.conf import settings

class Lead(models.Model):
    STATUS = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name