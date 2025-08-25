from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from .rig import RecordStatus


class WellBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    campaign_id: str
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_td_m: Optional[Decimal] = None
    actual_td_m: Optional[Decimal] = None


class WellCreate(WellBase):
    pass


class WellUpdate(BaseModel):
    name: Optional[str] = None
    campaign_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_td_m: Optional[Decimal] = None
    actual_td_m: Optional[Decimal] = None


class WellOut(WellBase):
    id: str
    created_at: datetime
    updated_at: datetime