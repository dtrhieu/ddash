from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import models

from core.models import Field, Platform, Rig, Well


class Scenario(models.Model):
    """A scenario version (draft vs approved) for planning purposes."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="scenarios"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Project(models.Model):
    """A single job instance (drill, workover, maintenance, etc.)."""

    class ProjectType(models.TextChoices):
        DRILLING = "drilling", "Drilling"
        WORKOVER = "workover", "Workover"
        PLUG_AND_ABANDON = "plug_and_abandon", "Plug And Abandon"
        FRACTURING = "fracturing", "Fracturing"
        PLATFORM_SERVICE = "platform_service", "Platform Service"
        UWILD = "uwild", "UWILD"
        RIG_OVERHAUL = "rig_overhaul", "Rig Overhaul"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETE = "complete", "Complete"
        ON_HOLD = "on_hold", "On Hold"
        CANCELED = "canceled", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        help_text="Optional field reference; can be derived from platform/well",
    )
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        help_text="Platform reference for platform-tied projects",
    )
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        help_text="Well reference for well-specific projects",
    )
    rig = models.ForeignKey(
        Rig,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        help_text="Rig assignment; required for certain project types",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    planned_start = models.DateField()
    planned_end = models.DateField()
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    dependencies = models.JSONField(
        default=dict, blank=True, help_text="Project dependencies as JSON"
    )
    extras = models.JSONField(
        default=dict, blank=True, help_text="Additional project metadata as JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["rig", "planned_start"]),
            models.Index(fields=["platform", "planned_start"]),
            models.Index(fields=["project_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"


class Campaign(models.Model):
    """A group of projects executed by a rig or field operations sequence."""

    class CampaignType(models.TextChoices):
        RIG_CAMPAIGN = "rig_campaign", "Rig Campaign"
        FIELD_OPERATIONS = "field_operations", "Field Operations"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255, unique=True)
    campaign_type = models.CharField(max_length=20, choices=CampaignType.choices)
    rig = models.ForeignKey(
        Rig,
        on_delete=models.CASCADE,
        related_name="campaigns",
        null=True,
        blank=True,
        help_text="Rig reference for rig campaigns",
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name="campaigns",
        null=True,
        blank=True,
        help_text="Field reference for field operations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["scenario"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"


class CampaignProject(models.Model):
    """Junction table for many-to-many relationship between Campaigns and Projects."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="campaign_projects"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="campaign_projects")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["campaign", "project"]]
        indexes = [
            models.Index(fields=["campaign"]),
            models.Index(fields=["project"]),
        ]

    def __str__(self):
        return f"{self.campaign.name} - {self.project.name}"


class CalcRun(models.Model):
    """Calculation runs for schedule metrics and conflict detection."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="calc_runs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    params = models.JSONField(default=dict, blank=True, help_text="Calculation parameters as JSON")
    results = models.JSONField(default=dict, blank=True, help_text="Calculation results as JSON")
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="calc_runs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["scenario"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"Calc run for {self.scenario.name} at {self.created_at} ({self.get_status_display()})"
        )
