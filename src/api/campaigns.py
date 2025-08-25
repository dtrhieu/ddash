from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from src.services.campaign_service import create_campaign, get_campaign, get_campaigns, update_campaign, delete_campaign
from typing import List

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_new_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    db_campaign = create_campaign(db, campaign)
    if not db_campaign:
        raise HTTPException(status_code=400, detail="Campaign could not be created")
    return db_campaign


@router.get("/", response_model=List[CampaignOut])
def read_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    campaigns = get_campaigns(db, skip=skip, limit=limit)
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignOut)
def read_campaign(campaign_id: str, db: Session = Depends(get_db)):
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign


@router.put("/{campaign_id}", response_model=CampaignOut)
def update_existing_campaign(campaign_id: str, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    db_campaign = update_campaign(db, campaign_id, campaign_update)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_campaign(campaign_id: str, db: Session = Depends(get_db)):
    db_campaign = delete_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return