from __future__ import annotations

from rest_framework import filters, viewsets

from .models import CalcRun, Campaign, CampaignProject, Project, Scenario
from .serializers import (
    CalcRunSerializer,
    CampaignProjectSerializer,
    CampaignSerializer,
    ProjectSerializer,
    ScenarioSerializer,
)


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.select_related("created_by").all().order_by("created_at")
    serializer_class = ScenarioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "status", "created_by__username"]
    ordering_fields = ["name", "status", "created_at"]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = (
        Project.objects.select_related("field", "platform", "well", "rig")
        .all()
        .order_by("planned_start")
    )
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "name",
        "project_type",
        "status",
        "field__name",
        "platform__name",
        "well__name",
        "rig__name",
    ]
    ordering_fields = ["planned_start", "planned_end", "created_at", "name"]


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related("scenario", "rig", "field").all().order_by("name")
    serializer_class = CampaignSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "campaign_type", "scenario__name", "rig__name", "field__name"]
    ordering_fields = ["name", "created_at"]


class CampaignProjectViewSet(viewsets.ModelViewSet):
    queryset = CampaignProject.objects.select_related("campaign", "project").all()
    serializer_class = CampaignProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["campaign__name", "project__name"]
    ordering_fields = ["created_at"]


class CalcRunViewSet(viewsets.ModelViewSet):
    queryset = (
        CalcRun.objects.select_related("scenario", "created_by").all().order_by("-created_at")
    )
    serializer_class = CalcRunSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["scenario__name", "status", "created_by__username"]
    ordering_fields = ["created_at", "completed_at"]
