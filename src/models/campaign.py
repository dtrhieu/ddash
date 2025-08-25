from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rig: str = Field(..., min_length=1, max_length=50)
    spud_date: date
    target_depth: float = Field(..., gt=0)
    current_depth: float = Field(..., ge=0)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    rig: Optional[str] = None
    spud_date: Optional[date] = None
    target_depth: Optional[float] = None
    current_depth: Optional[float] = None


class CampaignOut(CampaignBase):
    id: int
    progress_pct: float
    days_elapsed: int
    last_updated: datetime