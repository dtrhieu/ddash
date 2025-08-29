from __future__ import annotations

from django.contrib import admin

from .models import AuditLog, Field, MaintenanceWindow, Platform, Rig, Well


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "field", "status", "created_at")
    list_filter = ("status", "field")
    search_fields = ("name", "field__name")
    ordering = ("field__name", "name")


@admin.register(Rig)
class RigAdmin(admin.ModelAdmin):
    list_display = ("name", "rig_kind", "status", "day_rate", "created_at")
    list_filter = ("rig_kind", "status")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ("name", "field", "platform", "well_kind", "type", "created_at")
    list_filter = ("well_kind", "type", "field")
    search_fields = ("name", "field__name", "platform__name")
    ordering = ("field__name", "name")


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    list_display = ("platform", "start_date", "end_date", "reason")
    list_filter = ("platform",)
    search_fields = ("platform__name", "reason")
    ordering = ("platform__name", "start_date")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("at", "user", "entity", "entity_id", "action")
    list_filter = ("action", "entity")
    search_fields = ("entity", "entity_id")
    ordering = ("-at",)
