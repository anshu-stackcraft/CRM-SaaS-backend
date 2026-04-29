from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "role", "is_active", "is_staff", "last_login")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-id",)

    fieldsets = BaseUserAdmin.fieldsets + (("CRM Access", {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("CRM Access", {"fields": ("role",)}),)
