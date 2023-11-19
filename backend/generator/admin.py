from django.contrib import admin

from generator.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # exclude = ("winery_name", )
    readonly_fields = ("winery_name", )
    list_display = ("id", "winery_name", "year_from", "year_to", "status", "created", "updated")