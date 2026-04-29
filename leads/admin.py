from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "status", "assigned_to", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone", "assigned_to__username")
    autocomplete_fields = ("assigned_to",)
    ordering = ("-id",)
