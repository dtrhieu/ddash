from __future__ import annotations

from django.contrib import admin

from .models import CalcRun, Campaign, CampaignProject, Project, Scenario


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_by", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "created_by__username")
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project_type",
        "status",
        "field",
        "platform",
        "well",
        "rig",
        "planned_start",
        "planned_end",
    )
    list_filter = ("project_type", "status", "field", "platform", "rig")
    search_fields = ("name", "field__name", "platform__name", "well__name", "rig__name")
    ordering = ("planned_start",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "campaign_type", "scenario", "rig", "field", "created_at")
    list_filter = ("campaign_type", "scenario")
    search_fields = ("name", "scenario__name", "rig__name", "field__name")
    ordering = ("name",)


@admin.register(CampaignProject)
class CampaignProjectAdmin(admin.ModelAdmin):
    list_display = ("campaign", "project", "created_at")
    list_filter = ("campaign",)
    search_fields = ("campaign__name", "project__name")


@admin.register(CalcRun)
class CalcRunAdmin(admin.ModelAdmin):
    list_display = ("scenario", "status", "created_by", "created_at", "completed_at")
    list_filter = ("status", "scenario")
    search_fields = ("scenario__name", "created_by__username")
    ordering = ("-created_at",)
