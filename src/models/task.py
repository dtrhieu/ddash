from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    backlog = "backlog"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.backlog
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    campaign_id: Optional[int] = Field(None, description="Link task to a campaign")
    well_id: Optional[str] = Field(None, description="Link task to a well")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class TaskCommentCreate(BaseModel):
    author: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)


class TaskComment(BaseModel):
    author: str
    message: str
    timestamp_utc: datetime


class TaskOut(TaskBase):
    id: str
    comments: List[TaskComment]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))