from sqlalchemy.orm import Session
from src.database.models import Well
from src.models.well import WellCreate, WellUpdate
import uuid
from typing import List, Optional


def get_well(db: Session, well_id: str):
    return db.query(Well).filter(Well.id == well_id).first()


def get_wells(db: Session, skip: int = 0, limit: int = 100, campaign_id: Optional[str] = None):
    query = db.query(Well)
    if campaign_id:
        query = query.filter(Well.campaign_id == campaign_id)
    return query.offset(skip).limit(limit).all()


def create_well(db: Session, well: WellCreate):
    db_well = Well(
        id=str(uuid.uuid4()),
        campaign_id=well.campaign_id,
        name=well.name,
        status=well.status,
        start_date=well.start_date,
        end_date=well.end_date,
        planned_td_m=well.planned_td_m,
        actual_td_m=well.actual_td_m
    )
    db.add(db_well)
    db.commit()
    db.refresh(db_well)
    return db_well


def update_well(db: Session, well_id: str, well_update: WellUpdate):
    db_well = get_well(db, well_id)
    if not db_well:
        return None
    
    update_data = well_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_well, key, value)
    
    db.commit()
    db.refresh(db_well)
    return db_well


def delete_well(db: Session, well_id: str):
    db_well = get_well(db, well_id)
    if not db_well:
        return None
    
    db.delete(db_well)
    db.commit()
    return db_well