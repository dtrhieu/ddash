from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Field(models.Model):
    """A collection of platforms and exploration wells within the same asset/area."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Platform(models.Model):
    """An offshore production oil platform (CPP/WHP/CPP-WHP, etc.)."""

    class Status(models.TextChoices):
        OPERATING = "operating", "Operating"
        MAINTENANCE = "maintenance", "Maintenance"
        SHUTDOWN = "shutdown", "Shutdown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="platforms")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        unique_together = [["field", "name"]]

    def __str__(self):
        return f"{self.field.name} - {self.name}"


class Rig(models.Model):
    """Jack-up drilling rigs or light workover rigs (LWI)."""

    class RigKind(models.TextChoices):
        JACKUP = "jackup", "Jackup"
        MMWU = "mmwu", "MMWU"
        HWU = "hwu", "HWU"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        STANDBY = "standby", "Standby"
        MAINTENANCE = "maintenance", "Maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    rig_kind = models.CharField(max_length=20, choices=RigKind.choices)
    day_rate = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Daily rate in currency units"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_rig_kind_display()})"


class Well(models.Model):
    """Either a well on a platform or an exploration well at an open location."""

    class WellKind(models.TextChoices):
        PLATFORM_WELL = "platform_well", "Platform Well"
        EXPLORATION_OPEN_LOCATION = (
            "exploration_open_location",
            "Exploration Open Location",
        )

    class Type(models.TextChoices):
        EXPLORATION = "exploration", "Exploration"
        DEVELOPMENT = "development", "Development"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="wells")
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name="wells",
        null=True,
        blank=True,
        help_text="Platform reference for platform wells; null for exploration open location",
    )
    well_kind = models.CharField(max_length=30, choices=WellKind.choices)
    type = models.CharField(max_length=20, choices=Type.choices)
    lat = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude for exploration wells",
    )
    lon = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude for exploration wells",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.name}"


class MaintenanceWindow(models.Model):
    """Platform yearly maintenance periods (shutdowns/turnarounds)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="maintenance_windows"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["platform", "start_date"]),
        ]

    def __str__(self):
        return f"{self.platform.name} maintenance: {self.start_date} - {self.end_date}"


class AuditLog(models.Model):
    """Audit trail of all entity changes."""

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    entity = models.CharField(max_length=255, help_text="Entity type (model name)")
    entity_id = models.UUIDField(help_text="ID of the affected entity")
    action = models.CharField(max_length=10, choices=Action.choices)
    before = models.JSONField(null=True, blank=True, help_text="Entity state before change")
    after = models.JSONField(null=True, blank=True, help_text="Entity state after change")
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["entity", "entity_id"]),
            models.Index(fields=["at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} {self.action} {self.entity} {self.entity_id} at {self.at}"
