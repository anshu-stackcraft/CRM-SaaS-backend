from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "assigned_to", "due_date", "completed")
    list_filter = ("completed", "due_date")
    search_fields = ("title", "description", "assigned_to__username")
    autocomplete_fields = ("assigned_to",)
    ordering = ("-id",)
