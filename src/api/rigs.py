from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.rig import RigCreate, RigOut, RigUpdate
from src.services.rig_service import create_rig, get_rig, get_rigs, update_rig, delete_rig
from typing import List

router = APIRouter(prefix="/rigs", tags=["rigs"])


@router.post("/", response_model=RigOut, status_code=status.HTTP_201_CREATED)
def create_new_rig(rig: RigCreate, db: Session = Depends(get_db)):
    db_rig = create_rig(db, rig)
    if not db_rig:
        raise HTTPException(status_code=400, detail="Rig could not be created")
    return db_rig


@router.get("/", response_model=List[RigOut])
def read_rigs(skip: int = 0, limit: int = 100, campaign_id: str = None, db: Session = Depends(get_db)):
    rigs = get_rigs(db, skip=skip, limit=limit, campaign_id=campaign_id)
    return rigs


@router.get("/{rig_id}", response_model=RigOut)
def read_rig(rig_id: str, db: Session = Depends(get_db)):
    db_rig = get_rig(db, rig_id)
    if not db_rig:
        raise HTTPException(status_code=404, detail="Rig not found")
    return db_rig


@router.put("/{rig_id}", response_model=RigOut)
def update_existing_rig(rig_id: str, rig_update: RigUpdate, db: Session = Depends(get_db)):
    db_rig = update_rig(db, rig_id, rig_update)
    if not db_rig:
        raise HTTPException(status_code=404, detail="Rig not found")
    return db_rig


@router.delete("/{rig_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_rig(rig_id: str, db: Session = Depends(get_db)):
    db_rig = delete_rig(db, rig_id)
    if not db_rig:
        raise HTTPException(status_code=404, detail="Rig not found")
    return