from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "email", "phone")
    search_fields = ("name", "company", "email", "phone")
    ordering = ("-id",)
