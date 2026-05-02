from django.contrib import admin
from .models import Client, ClientImportFile


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mac_address", "phone", "country", "is_active", "action", "created_at")
    search_fields = ("name", "mac_address", "phone", "country", "comments")
    list_filter = ("is_active", "action", "country", "created_at")
    ordering = ("-id",)


@admin.register(ClientImportFile)
class ClientImportFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "uploaded_by", "created_count", "updated_count", "total_rows", "created_at")
    search_fields = ("original_name", "uploaded_by__username")
    ordering = ("-id",)
