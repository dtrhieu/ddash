from fastapi import APIRouter
from src.services.mock_services import get_campaigns, get_campaign_progress, get_campaign_days_elapsed, get_campaign_status, get_rigs
from typing import List, Dict, Any

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_dashboard_overview():
    # For mock implementation, we don't actually use a database session
    # Get all campaigns
    campaigns = get_campaigns(None)
    
    # Calculate overview metrics
    total_campaigns = len(campaigns)
    active_campaigns = [c for c in campaigns if get_campaign_status(c) != "Completed"]
    
    # Get rig information
    rigs = get_rigs(None)
    
    # Prepare rig status data
    rig_status_data = []
    for rig in rigs:
        campaign = next((c for c in campaigns if str(c.id) == str(rig.campaign_id)), None)
        rig_status_data.append({
            "rig_id": str(rig.id),
            "rig_name": rig.name,
            "campaign_id": str(rig.campaign_id) if campaign else None,
            "campaign_name": campaign.name if campaign else None,
            "status": rig.status or "Unknown"
        })
    
    # Prepare KPI data
    kpi_data = []
    for campaign in campaigns:
        kpi_data.append({
            "campaign_id": str(campaign.id),
            "campaign_name": campaign.name,
            "progress_pct": get_campaign_progress(campaign),
            "days_elapsed": get_campaign_days_elapsed(campaign),
            "status": get_campaign_status(campaign)
        })
    
    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": len(active_campaigns),
        "rigs": rig_status_data,
        "kpis": kpi_data
    }


@router.get("/kpis")
def get_kpi_data():
    # For mock implementation, we don't actually use a database session
    campaigns = get_campaigns(None)
    
    kpi_data = []
    for campaign in campaigns:
        kpi_data.append({
            "campaign_id": str(campaign.id),
            "campaign_name": campaign.name,
            "progress_pct": get_campaign_progress(campaign),
            "days_elapsed": get_campaign_days_elapsed(campaign),
            "status": get_campaign_status(campaign)
        })
    
    return kpi_data


@router.get("/alerts")
def get_alerts():
    # This is a placeholder for alert functionality
    # In a real implementation, this would check for:
    # - Overdue tasks
    # - Equipment issues
    # - Delays in campaign progress
    # - Pending approvals
    
    alerts = []
    # Example alert logic would go here
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }