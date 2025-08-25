from datetime import date, datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field, model_validator


# ------------------------------------------------------------
# Simple in-memory MVP for Drilling Campaign Management
# ------------------------------------------------------------
# Authentication/authorization: send header X-Role with one of
# Admin | Manager | Engineer
# ------------------------------------------------------------


ALLOWED_ROLES = {"Admin", "Manager", "Engineer"}


def get_role(x_role: Optional[str] = Header(default="Engineer")) -> str:
    if not x_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Role header")
    role = x_role.strip()
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role '{role}'. Use one of: {sorted(ALLOWED_ROLES)}")
    return role


def require_role(allowed: List[str]):
    def _checker(role: str = Depends(get_role)):
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{role}' is not allowed for this action")
        return role

    return _checker


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


# --------------- Campaign Models ---------------
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1)
    rig: str = Field(..., min_length=1)
    spud_date: date
    target_depth: int = Field(..., gt=0, description="Target depth in meters")
    current_depth: int = Field(0, ge=0, description="Current drilled depth in meters")

    @model_validator(mode="after")
    def _check_depths(self):
        if self.current_depth > self.target_depth:
            raise ValueError("current_depth cannot exceed target_depth")
        return self


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    rig: Optional[str] = None
    spud_date: Optional[date] = None
    target_depth: Optional[int] = Field(None, gt=0)
    current_depth: Optional[int] = Field(None, ge=0)


class CampaignOut(CampaignBase):
    id: int
    progress_pct: int
    days_elapsed: int
    status: str


# --------------- Task & Comment Models ---------------
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    campaign_id: Optional[int] = Field(None, description="Link task to a campaign")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
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
    id: int
    comments: List[TaskComment]


# --------------- Storage ---------------
class _CampaignStore:
    def __init__(self):
        self._data: Dict[int, CampaignBase] = {}
        self._id_seq = 1

    def add(self, item: CampaignBase) -> int:
        new_id = self._id_seq
        self._data[new_id] = item
        self._id_seq += 1
        return new_id

    def get(self, cid: int) -> CampaignBase:
        if cid not in self._data:
            raise KeyError
        return self._data[cid]

    def update(self, cid: int, item: CampaignBase):
        self._data[cid] = item

    def delete(self, cid: int):
        del self._data[cid]

    def items(self):
        return self._data.items()


class _TaskStore:
    def __init__(self):
        self._data: Dict[int, TaskOut] = {}
        self._id_seq = 1

    def add(self, item: TaskOut) -> int:
        new_id = self._id_seq
        self._data[new_id] = item
        self._id_seq += 1
        return new_id

    def get(self, tid: int) -> TaskOut:
        if tid not in self._data:
            raise KeyError
        return self._data[tid]

    def update(self, tid: int, item: TaskOut):
        self._data[tid] = item

    def delete(self, tid: int):
        del self._data[tid]

    def items(self):
        return self._data.items()


campaigns = _CampaignStore()
tasks = _TaskStore()


def to_campaign_out(cid: int, c: CampaignBase) -> CampaignOut:
    progress = int(round((c.current_depth / c.target_depth) * 100)) if c.target_depth > 0 else 0
    days = (date.today() - c.spud_date).days
    status_str = "Completed" if c.current_depth >= c.target_depth else "Drilling"
    return CampaignOut(id=cid, name=c.name, rig=c.rig, spud_date=c.spud_date,
                       target_depth=c.target_depth, current_depth=c.current_depth,
                       progress_pct=progress, days_elapsed=days, status=status_str)


# --------------- App ---------------
app = FastAPI(title="Drilling Campaign Management - MVP", version="0.1.0")


@app.get("/")
def root():
    return {
        "name": "Drilling Campaign Management - MVP",
        "version": "0.1.0",
        "docs": "/docs",
        "auth": "Send header X-Role: Admin | Manager | Engineer",
    }


# --------------- Campaign Endpoints ---------------
@app.post("/campaigns", response_model=CampaignOut, dependencies=[Depends(require_role(["Admin", "Manager"]))])
def create_campaign(payload: CampaignCreate):
    cid = campaigns.add(payload)
    return to_campaign_out(cid, campaigns.get(cid))


@app.get("/campaigns", response_model=List[CampaignOut])
def list_campaigns(role: str = Depends(get_role)):
    return [to_campaign_out(cid, c) for cid, c in campaigns.items()]


@app.get("/campaigns/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, role: str = Depends(get_role)):
    try:
        c = campaigns.get(campaign_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return to_campaign_out(campaign_id, c)


@app.patch("/campaigns/{campaign_id}", response_model=CampaignOut, dependencies=[Depends(require_role(["Admin", "Manager"]))])
def update_campaign(campaign_id: int, payload: CampaignUpdate):
    try:
        current = campaigns.get(campaign_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Campaign not found")

    updated = current.model_copy(update={k: v for k, v in payload.model_dump(exclude_unset=True).items()})

    # Cross-field validation: current_depth <= target_depth
    if updated.current_depth > updated.target_depth:
        raise HTTPException(status_code=400, detail="current_depth cannot exceed target_depth")

    campaigns.update(campaign_id, updated)
    return to_campaign_out(campaign_id, updated)


@app.delete("/campaigns/{campaign_id}", status_code=204, dependencies=[Depends(require_role(["Admin"]))])
def delete_campaign(campaign_id: int):
    try:
        campaigns.delete(campaign_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Campaign not found")


# --------------- Task Endpoints ---------------
@app.post("/tasks", response_model=TaskOut, dependencies=[Depends(require_role(["Admin", "Manager", "Engineer"]))])
def create_task(payload: TaskCreate):
    if payload.campaign_id is not None:
        # Validate campaign exists if referenced
        try:
            campaigns.get(payload.campaign_id)
        except KeyError:
            raise HTTPException(status_code=400, detail="Referenced campaign_id does not exist")

    task = TaskOut(**payload.model_dump(), id=0, comments=[])
    tid = tasks.add(task)
    created = tasks.get(tid)
    created.id = tid
    tasks.update(tid, created)
    return created


@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(campaign_id: Optional[int] = None, status_filter: Optional[TaskStatus] = None, role: str = Depends(get_role)):
    result: List[TaskOut] = []
    for tid, task in tasks.items():
        if campaign_id is not None and task.campaign_id != campaign_id:
            continue
        if status_filter is not None and task.status != status_filter:
            continue
        result.append(task)
    return result


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, role: str = Depends(get_role)):
    try:
        return tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}", response_model=TaskOut, dependencies=[Depends(require_role(["Admin", "Manager", "Engineer"]))])
def update_task(task_id: int, payload: TaskUpdate):
    try:
        current = tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")

    updated = current.model_copy(update={k: v for k, v in payload.model_dump(exclude_unset=True).items()})
    tasks.update(task_id, updated)
    return updated


@app.delete("/tasks/{task_id}", status_code=204, dependencies=[Depends(require_role(["Admin", "Manager"]))])
def delete_task(task_id: int):
    try:
        tasks.delete(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks/{task_id}/comments", response_model=TaskOut, dependencies=[Depends(require_role(["Admin", "Manager", "Engineer"]))])
def add_comment(task_id: int, payload: TaskCommentCreate):
    try:
        task = tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = TaskComment(author=payload.author, message=payload.message, timestamp_utc=datetime.now(timezone.utc))
    task.comments.append(comment)
    tasks.update(task_id, task)
    return task


# --------------- Dashboard ---------------
@app.get("/dashboard")
def dashboard(role: str = Depends(get_role)):
    all_camps = [to_campaign_out(cid, c) for cid, c in campaigns.items()]
    active = [c for c in all_camps if c.status != "Completed"]

    rigs = [
        {
            "campaign_id": c.id,
            "campaign": c.name,
            "rig": c.rig,
            "status": c.status,
        }
        for c in all_camps
    ]

    return {
        "date": datetime.now(timezone.utc).isoformat(),
        "campaigns_total": len(all_camps),
        "active_campaigns": len(active),
        "rigs": rigs,
        "kpis": [
            {
                "campaign_id": c.id,
                "name": c.name,
                "progress_pct": c.progress_pct,
                "days_elapsed": c.days_elapsed,
                "depth": {"current": c.current_depth, "target": c.target_depth},
            }
            for c in all_camps
        ],
    }


# --------------- Seed Data ---------------
@app.on_event("startup")
def seed():
    if not list(campaigns.items()):
        c1 = CampaignCreate(name="Alpha-1", rig="Rig 7", spud_date=date.today(), target_depth=3000, current_depth=1200)
        c2 = CampaignCreate(name="Bravo-2", rig="Rig 3", spud_date=date.today(), target_depth=2500, current_depth=2500)
        id1 = campaigns.add(c1)
        id2 = campaigns.add(c2)
        # Seed tasks
        t1 = TaskOut(id=0, title="BOP Test", description="Perform BOP pressure test", status=TaskStatus.in_progress,
                     due_date=date.today(), assigned_to="eng1", campaign_id=id1, comments=[])
        t2 = TaskOut(id=0, title="Mobilize Mud Logging", description=None, status=TaskStatus.todo,
                     due_date=None, assigned_to=None, campaign_id=id1, comments=[])
        tid1 = tasks.add(t1)
        tasks.get(tid1).id = tid1
        tasks.update(tid1, tasks.get(tid1))
        tid2 = tasks.add(t2)
        tasks.get(tid2).id = tid2
        tasks.update(tid2, tasks.get(tid2))


# To run locally:
#   1) pip install -r requirements.txt
#   2) uvicorn main:app --reload
#   Or: python main.py

if __name__ == "__main__":
    # Allow running via: python main.py
    import os
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", "8000")), reload=True)
