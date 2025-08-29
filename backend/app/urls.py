"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.utils.timezone import now
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from core.views import (
    FieldViewSet,
    MaintenanceWindowViewSet,
    PlatformViewSet,
    RigViewSet,
    WellViewSet,
)
from scheduling.views import (
    CalcRunViewSet,
    CampaignProjectViewSet,
    CampaignViewSet,
    ProjectViewSet,
    ScenarioViewSet,
)


@api_view(["GET"])
def health(request):
    """Simple health endpoint for smoke testing.

    Returns a small JSON payload without touching the database so it is safe
    to call even before migrations are applied.
    """
    return Response(
        {
            "ok": True,
            "service": "ddash-backend",
            "time": now().isoformat(),
            "version": "M1-dev",
        }
    )


router = DefaultRouter()
# Core endpoints
router.register(r"fields", FieldViewSet, basename="field")
router.register(r"platforms", PlatformViewSet, basename="platform")
router.register(r"rigs", RigViewSet, basename="rig")
router.register(r"wells", WellViewSet, basename="well")
router.register(r"maintenance-windows", MaintenanceWindowViewSet, basename="maintenancewindow")
# Scheduling endpoints
router.register(r"scenarios", ScenarioViewSet, basename="scenario")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"campaign-projects", CampaignProjectViewSet, basename="campaignproject")
router.register(r"calc-runs", CalcRunViewSet, basename="calcrun")


# Simple schema-lite endpoint to list available routes without extra deps
@api_view(["GET"])
def schema_lite(request):
    endpoints = []
    for url in router.urls:
        try:
            # Django 5 patterns have "pattern" attr convertible to str
            pattern = str(url.pattern)
        except Exception:  # pragma: no cover - defensive
            pattern = getattr(url, "name", "")
        endpoints.append(
            {
                "name": url.name,
                "pattern": pattern,
                "lookup": getattr(url, "lookup_value_regex", None),
            }
        )
    return Response(
        {
            "service": "ddash-backend",
            "count": len(endpoints),
            "endpoints": endpoints,
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health),  # M1.1.6 health endpoint
    path("api/", include(router.urls)),
    path("api/schema-lite", schema_lite, name="api-schema-lite"),
    path(
        "api/docs/",
        TemplateView.as_view(
            template_name="api_docs.html",
            extra_context={"endpoints": [str(u.pattern) for u in router.urls]},
        ),
        name="api-docs",
    ),
]
