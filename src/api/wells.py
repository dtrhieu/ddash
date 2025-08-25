from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.well import WellCreate, WellOut, WellUpdate
from src.services.well_service import create_well, get_well, get_wells, update_well, delete_well
from typing import List

router = APIRouter(prefix="/wells", tags=["wells"])


@router.post("/", response_model=WellOut, status_code=status.HTTP_201_CREATED)
def create_new_well(well: WellCreate, db: Session = Depends(get_db)):
    db_well = create_well(db, well)
    if not db_well:
        raise HTTPException(status_code=400, detail="Well could not be created")
    return db_well


@router.get("/", response_model=List[WellOut])
def read_wells(skip: int = 0, limit: int = 100, campaign_id: str = None, db: Session = Depends(get_db)):
    wells = get_wells(db, skip=skip, limit=limit, campaign_id=campaign_id)
    return wells


@router.get("/{well_id}", response_model=WellOut)
def read_well(well_id: str, db: Session = Depends(get_db)):
    db_well = get_well(db, well_id)
    if not db_well:
        raise HTTPException(status_code=404, detail="Well not found")
    return db_well


@router.put("/{well_id}", response_model=WellOut)
def update_existing_well(well_id: str, well_update: WellUpdate, db: Session = Depends(get_db)):
    db_well = update_well(db, well_id, well_update)
    if not db_well:
        raise HTTPException(status_code=404, detail="Well not found")
    return db_well


@router.delete("/{well_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_well(well_id: str, db: Session = Depends(get_db)):
    db_well = delete_well(db, well_id)
    if not db_well:
        raise HTTPException(status_code=404, detail="Well not found")
    return