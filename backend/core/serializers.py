from __future__ import annotations

from rest_framework import serializers

from .models import Field, MaintenanceWindow, Platform, Rig, Well


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["id", "field", "name", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class RigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rig
        fields = ["id", "name", "rig_kind", "day_rate", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class WellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = [
            "id",
            "name",
            "field",
            "platform",
            "well_kind",
            "type",
            "lat",
            "lon",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Basic cross-field validation aligned with model intent
        well_kind = attrs.get("well_kind", getattr(self.instance, "well_kind", None))
        platform = attrs.get("platform", getattr(self.instance, "platform", None))
        lat = attrs.get("lat", getattr(self.instance, "lat", None))
        lon = attrs.get("lon", getattr(self.instance, "lon", None))

        if well_kind == Well.WellKind.PLATFORM_WELL and platform is None:
            raise serializers.ValidationError(
                {"platform": "Platform well must reference a platform."}
            )
        if well_kind == Well.WellKind.EXPLORATION_OPEN_LOCATION and platform is not None:
            raise serializers.ValidationError(
                {"platform": "Exploration open location must not reference a platform."}
            )
        if well_kind == Well.WellKind.EXPLORATION_OPEN_LOCATION and (lat is None or lon is None):
            raise serializers.ValidationError(
                {
                    "lat": "Exploration well requires lat/lon.",
                    "lon": "Exploration well requires lat/lon.",
                }
            )
        return attrs


class MaintenanceWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceWindow
        fields = [
            "id",
            "platform",
            "start_date",
            "end_date",
            "reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        platform = attrs.get("platform", getattr(self.instance, "platform", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "end_date must be on or after start_date."}
            )
        # Prevent overlapping maintenance windows for the same platform
        if platform and start and end:
            qs = MaintenanceWindow.objects.filter(platform=platform)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            overlap = qs.filter(start_date__lte=end, end_date__gte=start).exists()
            if overlap:
                raise serializers.ValidationError(
                    {"start_date": "Overlaps another maintenance window for this platform."}
                )
        return attrs
