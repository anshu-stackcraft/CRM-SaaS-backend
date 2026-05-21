import random
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


def _generate_4digit_emp_id():
    while True:
        candidate = f"{random.randint(0, 9999):04d}"
        if not EmployeeProfile.objects.filter(emp_id=candidate).exists():
            return candidate


class Team(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")
    emp_id = models.CharField(
        max_length=4,
        unique=True,
        blank=True,
        validators=[RegexValidator(regex=r"^\d{4}$", message="Employee ID must be exactly 4 digits.")],
    )
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.emp_id:
            self.emp_id = _generate_4digit_emp_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.emp_id} - {self.user.username}"
