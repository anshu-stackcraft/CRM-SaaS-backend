from django.contrib import admin

from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("client__name", "client__company", "status")
    autocomplete_fields = ("client",)
    ordering = ("-id",)
