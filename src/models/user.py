from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    admin = "admin"
    ops_manager = "ops_manager"
    engineer = "engineer"
    logistics = "logistics"
    executive = "executive"


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    name: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = "UTC"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    active: Optional[bool] = None


class UserOut(UserBase):
    id: str
    active: bool
    roles: List[UserRole]
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    roles: List[UserRole]