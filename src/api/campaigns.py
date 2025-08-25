from fastapi import APIRouter, HTTPException, status
from src.models.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from src.services.mock_services import create_campaign, get_campaign, get_campaigns, update_campaign, delete_campaign
from typing import List

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_new_campaign(campaign: CampaignCreate):
    # For mock implementation, we don't actually use a database session
    db_campaign = create_campaign(None, campaign)
    if not db_campaign:
        raise HTTPException(status_code=400, detail="Campaign could not be created")
    return db_campaign


@router.get("/", response_model=List[CampaignOut])
def read_campaigns(skip: int = 0, limit: int = 100):
    # For mock implementation, we don't actually use a database session
    campaigns = get_campaigns(None, skip=skip, limit=limit)
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignOut)
def read_campaign(campaign_id: int):
    # For mock implementation, we don't actually use a database session
    db_campaign = get_campaign(None, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign


@router.put("/{campaign_id}", response_model=CampaignOut)
def update_existing_campaign(campaign_id: int, campaign_update: CampaignUpdate):
    # For mock implementation, we don't actually use a database session
    db_campaign = update_campaign(None, campaign_id, campaign_update)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_campaign(campaign_id: int):
    # For mock implementation, we don't actually use a database session
    db_campaign = delete_campaign(None, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return