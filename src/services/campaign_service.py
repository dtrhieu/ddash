from sqlalchemy.orm import Session
from src.database.models import Campaign
from src.models.campaign import CampaignCreate, CampaignUpdate
from datetime import date, datetime
import uuid
from typing import List, Optional


def get_campaign(db: Session, campaign_id: str):
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Campaign).offset(skip).limit(limit).all()


def create_campaign(db: Session, campaign: CampaignCreate):
    db_campaign = Campaign(
        id=str(uuid.uuid4()),
        name=campaign.name,
        block=campaign.block,
        field=campaign.field,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        status=campaign.status
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update_campaign(db: Session, campaign_id: str, campaign_update: CampaignUpdate):
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return None
    
    update_data = campaign_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)
    
    db_campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def delete_campaign(db: Session, campaign_id: str):
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return None
    
    db.delete(db_campaign)
    db.commit()
    return db_campaign


def get_campaign_progress(campaign: Campaign) -> float:
    """
    Calculate campaign progress percentage.
    """
    if campaign.target_depth and campaign.target_depth > 0:
        return round((campaign.current_depth / campaign.target_depth) * 100, 2)
    return 0.0


def get_campaign_days_elapsed(campaign: Campaign) -> int:
    """
    Calculate days elapsed since campaign start.
    """
    if campaign.start_date:
        return (date.today() - campaign.start_date).days
    return 0


def get_campaign_status(campaign: Campaign) -> str:
    """
    Determine campaign status based on progress.
    """
    if campaign.current_depth >= campaign.target_depth:
        return "Completed"
    elif campaign.current_depth > 0:
        return "In Progress"
    else:
        return "Not Started"