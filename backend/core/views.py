from __future__ import annotations

from rest_framework import filters, viewsets

from .models import Field, MaintenanceWindow, Platform, Rig, Well
from .serializers import (
    FieldSerializer,
    MaintenanceWindowSerializer,
    PlatformSerializer,
    RigSerializer,
    WellSerializer,
)


class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all().order_by("name")
    serializer_class = FieldSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class PlatformViewSet(viewsets.ModelViewSet):
    queryset = Platform.objects.select_related("field").all().order_by("name")
    serializer_class = PlatformSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "field__name"]
    ordering_fields = ["name", "created_at"]


class RigViewSet(viewsets.ModelViewSet):
    queryset = Rig.objects.all().order_by("name")
    serializer_class = RigSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "rig_kind", "status"]
    ordering_fields = ["name", "day_rate", "created_at"]


class WellViewSet(viewsets.ModelViewSet):
    queryset = Well.objects.select_related("field", "platform").all().order_by("name")
    serializer_class = WellSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "field__name", "platform__name", "well_kind", "type"]
    ordering_fields = ["name", "created_at"]


class MaintenanceWindowViewSet(viewsets.ModelViewSet):
    queryset = (
        MaintenanceWindow.objects.select_related("platform")
        .all()
        .order_by("platform__name", "start_date")
    )
    serializer_class = MaintenanceWindowSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["platform__name", "reason"]
    ordering_fields = ["start_date", "end_date", "created_at"]
