from __future__ import annotations

from rest_framework import serializers

from .models import CalcRun, Campaign, CampaignProject, Project, Scenario


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ["id", "name", "status", "created_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "project_type",
            "field",
            "platform",
            "well",
            "rig",
            "status",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "dependencies",
            "extras",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Basic temporal validation: planned_end >= planned_start
        start = attrs.get("planned_start", getattr(self.instance, "planned_start", None))
        end = attrs.get("planned_end", getattr(self.instance, "planned_end", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"planned_end": "planned_end must be on or after planned_start."}
            )
        return attrs


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "scenario",
            "name",
            "campaign_type",
            "rig",
            "field",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        ctype = attrs.get("campaign_type", getattr(self.instance, "campaign_type", None))
        rig = attrs.get("rig", getattr(self.instance, "rig", None))
        field = attrs.get("field", getattr(self.instance, "field", None))
        errors = {}
        if ctype == Campaign.CampaignType.RIG_CAMPAIGN:
            if rig is None:
                errors["rig"] = "Rig campaign requires a rig."
            if field is not None:
                errors["field"] = "Rig campaign must not set a field."
        elif ctype == Campaign.CampaignType.FIELD_OPERATIONS:
            if field is None:
                errors["field"] = "Field operations require a field."
            if rig is not None:
                errors["rig"] = "Field operations must not set a rig."
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class CampaignProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignProject
        fields = ["id", "campaign", "project", "created_at"]
        read_only_fields = ["id", "created_at"]


class CalcRunSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CalcRun
        fields = [
            "id",
            "scenario",
            "status",
            "params",
            "results",
            "created_by",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["id", "created_at"]
