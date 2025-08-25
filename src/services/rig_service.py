from sqlalchemy.orm import Session
from src.database.models import Rig
from src.models.rig import RigCreate, RigUpdate
import uuid
from typing import List, Optional


def get_rig(db: Session, rig_id: str):
    return db.query(Rig).filter(Rig.id == rig_id).first()


def get_rigs(db: Session, skip: int = 0, limit: int = 100, campaign_id: Optional[str] = None):
    query = db.query(Rig)
    if campaign_id:
        query = query.filter(Rig.campaign_id == campaign_id)
    return query.offset(skip).limit(limit).all()


def create_rig(db: Session, rig: RigCreate):
    db_rig = Rig(
        id=str(uuid.uuid4()),
        campaign_id=rig.campaign_id,
        name=rig.name,
        type=rig.type,
        lat=rig.lat,
        lon=rig.lon,
        status=rig.status,
        notes=rig.notes
    )
    db.add(db_rig)
    db.commit()
    db.refresh(db_rig)
    return db_rig


def update_rig(db: Session, rig_id: str, rig_update: RigUpdate):
    db_rig = get_rig(db, rig_id)
    if not db_rig:
        return None
    
    update_data = rig_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rig, key, value)
    
    db.commit()
    db.refresh(db_rig)
    return db_rig


def delete_rig(db: Session, rig_id: str):
    db_rig = get_rig(db, rig_id)
    if not db_rig:
        return None
    
    db.delete(db_rig)
    db.commit()
    return db_rig