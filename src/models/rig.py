from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RigType(str, Enum):
    jackup = "jackup"
    semisub = "semisub"
    drillship = "drillship"


class RecordStatus(str, Enum):
    active = "active"
    archived = "archived"


class RigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: RigType
    campaign_id: str
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    status: Optional[str] = None
    notes: Optional[str] = None


class RigCreate(RigBase):
    pass


class RigUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[RigType] = None
    campaign_id: Optional[str] = None
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    status: Optional[str] = None
    notes: Optional[str] = None


class RigOut(RigBase):
    id: str
    created_at: datetime
    updated_at: datetime