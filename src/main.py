from datetime import date, datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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


# --------------- UI: CRUD for Campaign, Rig, Well ---------------
from uuid import uuid4

class RigType(str, Enum):
    jackup = "jackup"
    semisub = "semisub"
    drillship = "drillship"

class RecordStatus(str, Enum):
    active = "active"
    archived = "archived"

class UICampaign(BaseModel):
    id: str
    name: str
    block: Optional[str] = None
    field: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    status: RecordStatus = RecordStatus.active
    createdBy: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UIRig(BaseModel):
    id: str
    campaignId: str
    name: str
    type: RigType
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    status: Optional[str] = None
    notes: Optional[str] = None

class UIWell(BaseModel):
    id: str
    campaignId: str
    name: str
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    plannedTdM: Optional[float] = Field(default=None, gt=0)
    actualTdM: Optional[float] = Field(default=None, ge=0)

# In-memory stores
ui_campaigns: Dict[str, UICampaign] = {}
ui_rigs: Dict[str, UIRig] = {}
ui_wells: Dict[str, UIWell] = {}


def _layout(title: str, body: str) -> HTMLResponse:
    html = f"""
    <html><head><title>{title}</title>
    <style>
      body {{ font-family: sans-serif; margin: 20px; }}
      nav a {{ margin-right: 12px; }}
      table {{ border-collapse: collapse; margin-top: 10px; }}
      th, td {{ border: 1px solid #ccc; padding: 6px 10px; }}
      form {{ margin: 8px 0; }}
      input, select, textarea {{ padding: 6px; margin: 4px; }}
      .danger {{ color: #b00; }}
    </style>
    </head><body>
      <nav>
        <a href="/ui">Home</a>
        <a href="/ui/campaigns">Campaigns</a>
        <a href="/ui/rigs">Rigs</a>
        <a href="/ui/wells">Wells</a>
      </nav>
      <h1>{title}</h1>
      {body}
    </body></html>
    """
    return HTMLResponse(content=html)

@app.get("/ui", response_class=HTMLResponse)
def ui_home():
    return _layout("UI Home", "<p>Use the navigation to manage Campaigns, Rigs, and Wells.</p>")

# -------- Campaign UI --------
@app.get("/ui/campaigns", response_class=HTMLResponse)
def ui_list_campaigns():
    rows = "".join(
        f"<tr><td>{c.name}</td><td>{c.block or ''}</td><td>{c.field or ''}</td><td>{c.status}</td>"
        f"<td><a href=\"/ui/campaigns/{cid}\">View</a></td></tr>"
        for cid, c in ui_campaigns.items()
    )
    body = f"""
    <a href="/ui/campaigns/new">+ New Campaign</a>
    <table>
      <tr><th>Name</th><th>Block</th><th>Field</th><th>Status</th><th>Actions</th></tr>
      {rows}
    </table>
    """
    return _layout("Campaigns", body)

@app.get("/ui/campaigns/new", response_class=HTMLResponse)
def ui_new_campaign_form():
    body = """
    <form method="post" action="/ui/campaigns/new">
      <label>Name <input name="name" required></label><br>
      <label>Block <input name="block"></label><br>
      <label>Field <input name="field"></label><br>
      <label>Start Date <input type="date" name="startDate"></label>
      <label>End Date <input type="date" name="endDate"></label><br>
      <label>Status
        <select name="status">
          <option value="active">active</option>
          <option value="archived">archived</option>
        </select>
      </label><br>
      <button type="submit">Create</button>
    </form>
    """
    return _layout("New Campaign", body)

@app.post("/ui/campaigns/new")
def ui_new_campaign(
    name: str = Form(...),
    block: Optional[str] = Form(None),
    field: Optional[str] = Form(None),
    startDate: Optional[str] = Form(None),
    endDate: Optional[str] = Form(None),
    status_val: str = Form(alias="status", default="active"),
):
    cid = str(uuid4())
    sd = date.fromisoformat(startDate) if startDate else None
    ed = date.fromisoformat(endDate) if endDate else None
    ui_campaigns[cid] = UICampaign(
        id=cid, name=name, block=block, field=field, startDate=sd, endDate=ed,
        status=RecordStatus(status_val)
    )
    return RedirectResponse(url=f"/ui/campaigns/{cid}", status_code=303)

@app.get("/ui/campaigns/{cid}", response_class=HTMLResponse)
def ui_view_campaign(cid: str):
    c = ui_campaigns.get(cid)
    if not c:
        return _layout("Not found", f"<p class=\"danger\">Campaign {cid} not found.</p>")
    rigs = [r for r in ui_rigs.values() if r.campaignId == cid]
    wells = [w for w in ui_wells.values() if w.campaignId == cid]
    rigs_list = "<ul>" + "".join(f"<li>{r.name} ({r.type})</li>" for r in rigs) + "</ul>"
    wells_list = "<ul>" + "".join(f"<li>{w.name}</li>" for w in wells) + "</ul>"
    body = f"""
      <p><b>Name:</b> {c.name}</p>
      <p><b>Block:</b> {c.block or ''} | <b>Field:</b> {c.field or ''}</p>
      <p><b>Status:</b> {c.status}</p>
      <p><b>Start:</b> {c.startDate or ''} | <b>End:</b> {c.endDate or ''}</p>
      <h3>Edit</h3>
      <form method="post" action="/ui/campaigns/{cid}/edit">
        <label>Name <input name="name" value="{c.name}" required></label><br>
        <label>Block <input name="block" value="{c.block or ''}"></label><br>
        <label>Field <input name="field" value="{c.field or ''}"></label><br>
        <label>Start Date <input type="date" name="startDate" value="{c.startDate or ''}"></label>
        <label>End Date <input type="date" name="endDate" value="{c.endDate or ''}"></label><br>
        <label>Status
          <select name="status">
            <option value="active" {'selected' if c.status==RecordStatus.active else ''}>active</option>
            <option value="archived" {'selected' if c.status==RecordStatus.archived else ''}>archived</option>
          </select>
        </label><br>
        <button type="submit">Save</button>
      </form>
      <form method="post" action="/ui/campaigns/{cid}/delete" onsubmit="return confirm('Delete campaign?')">
        <button type="submit" class="danger">Delete</button>
      </form>
      <h3>Rigs</h3>
      {rigs_list}
      <p><a href="/ui/rigs/new?campaignId={cid}">+ Add Rig</a></p>
      <h3>Wells</h3>
      {wells_list}
      <p><a href="/ui/wells/new?campaignId={cid}">+ Add Well</a></p>
    """
    return _layout(f"Campaign: {c.name}", body)

@app.post("/ui/campaigns/{cid}/edit")
def ui_edit_campaign(cid: str,
                     name: str = Form(...),
                     block: Optional[str] = Form(None),
                     field: Optional[str] = Form(None),
                     startDate: Optional[str] = Form(None),
                     endDate: Optional[str] = Form(None),
                     status_val: str = Form(alias="status", default="active")):
    c = ui_campaigns.get(cid)
    if not c:
        raise HTTPException(404, "Campaign not found")
    c.name = name
    c.block = block
    c.field = field
    c.startDate = date.fromisoformat(startDate) if startDate else None
    c.endDate = date.fromisoformat(endDate) if endDate else None
    c.status = RecordStatus(status_val)
    c.updatedAt = datetime.now(timezone.utc)
    ui_campaigns[cid] = c
    return RedirectResponse(url=f"/ui/campaigns/{cid}", status_code=303)

@app.post("/ui/campaigns/{cid}/delete")
def ui_delete_campaign(cid: str):
    # Cascade delete rigs and wells that belong to this campaign
    to_del_r = [rid for rid, r in ui_rigs.items() if r.campaignId == cid]
    to_del_w = [wid for wid, w in ui_wells.items() if w.campaignId == cid]
    for rid in to_del_r: ui_rigs.pop(rid, None)
    for wid in to_del_w: ui_wells.pop(wid, None)
    ui_campaigns.pop(cid, None)
    return RedirectResponse(url="/ui/campaigns", status_code=303)

# -------- Rig UI --------
@app.get("/ui/rigs", response_class=HTMLResponse)
def ui_list_rigs():
    def camp_name(cid: str) -> str:
        c = ui_campaigns.get(cid)
        return c.name if c else "?"
    rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.type}</td><td>{camp_name(r.campaignId)}</td>"
        f"<td><a href=\"/ui/rigs/{rid}\">View</a></td></tr>"
        for rid, r in ui_rigs.items()
    )
    body = f"""
    <a href="/ui/rigs/new">+ New Rig</a>
    <table>
      <tr><th>Name</th><th>Type</th><th>Campaign</th><th>Actions</th></tr>
      {rows}
    </table>
    """
    return _layout("Rigs", body)

@app.get("/ui/rigs/new", response_class=HTMLResponse)
def ui_new_rig_form(campaignId: Optional[str] = None):
    options = "".join(
        f"<option value=\"{cid}\" {'selected' if campaignId==cid else ''}>{c.name}</option>"
        for cid, c in ui_campaigns.items()
    )
    body = f"""
    <form method="post" action="/ui/rigs/new">
      <label>Campaign
        <select name="campaignId" required>{options}</select>
      </label><br>
      <label>Name <input name="name" required></label>
      <label>Type
        <select name="type">
          <option value="jackup">jackup</option>
          <option value="semisub">semisub</option>
          <option value="drillship">drillship</option>
        </select>
      </label><br>
      <label>Lat <input type="number" step="0.000001" name="lat"></label>
      <label>Lon <input type="number" step="0.000001" name="lon"></label><br>
      <label>Status <input name="status"></label><br>
      <label>Notes <textarea name="notes"></textarea></label><br>
      <button type="submit">Create</button>
    </form>
    """
    return _layout("New Rig", body)

@app.post("/ui/rigs/new")
def ui_new_rig(
    campaignId: str = Form(...),
    name: str = Form(...),
    type_val: str = Form(..., alias="type"),
    lat: Optional[str] = Form(None),
    lon: Optional[str] = Form(None),
    status_text: Optional[str] = Form(alias="status", default=None),
    notes: Optional[str] = Form(None),
):
    if campaignId not in ui_campaigns:
        raise HTTPException(400, "Invalid campaignId")
    rid = str(uuid4())
    ui_rigs[rid] = UIRig(
        id=rid,
        campaignId=campaignId,
        name=name,
        type=RigType(type_val),
        lat=float(lat) if lat else None,
        lon=float(lon) if lon else None,
        status=status_text,
        notes=notes,
    )
    return RedirectResponse(url=f"/ui/rigs/{rid}", status_code=303)

@app.get("/ui/rigs/{rid}", response_class=HTMLResponse)
def ui_view_rig(rid: str):
    r = ui_rigs.get(rid)
    if not r:
        return _layout("Not found", f"<p class=\"danger\">Rig {rid} not found.</p>")
    options = "".join(
        f"<option value=\"{cid}\" {'selected' if cid==r.campaignId else ''}>{c.name}</option>"
        for cid, c in ui_campaigns.items()
    )
    body = f"""
      <p><b>Name:</b> {r.name} | <b>Type:</b> {r.type}</p>
      <p><b>Campaign:</b> {ui_campaigns.get(r.campaignId).name if ui_campaigns.get(r.campaignId) else '?'}</p>
      <p><b>Lat/Lon:</b> {r.lat or ''} , {r.lon or ''}</p>
      <p><b>Status:</b> {r.status or ''}</p>
      <p><b>Notes:</b> {r.notes or ''}</p>
      <h3>Edit</h3>
      <form method="post" action="/ui/rigs/{rid}/edit">
        <label>Campaign <select name="campaignId" required>{options}</select></label><br>
        <label>Name <input name="name" value="{r.name}" required></label>
        <label>Type
          <select name="type">
            <option value="jackup" {'selected' if r.type==RigType.jackup else ''}>jackup</option>
            <option value="semisub" {'selected' if r.type==RigType.semisub else ''}>semisub</option>
            <option value="drillship" {'selected' if r.type==RigType.drillship else ''}>drillship</option>
          </select>
        </label><br>
        <label>Lat <input type="number" step="0.000001" name="lat" value="{r.lat or ''}"></label>
        <label>Lon <input type="number" step="0.000001" name="lon" value="{r.lon or ''}"></label><br>
        <label>Status <input name="status" value="{r.status or ''}"></label><br>
        <label>Notes <textarea name="notes">{r.notes or ''}</textarea></label><br>
        <button type="submit">Save</button>
      </form>
      <form method="post" action="/ui/rigs/{rid}/delete" onsubmit="return confirm('Delete rig?')">
        <button type="submit" class="danger">Delete</button>
      </form>
    """
    return _layout(f"Rig: {r.name}", body)

@app.post("/ui/rigs/{rid}/edit")
def ui_edit_rig(rid: str,
                campaignId: str = Form(...),
                name: str = Form(...),
                type_val: str = Form(..., alias="type"),
                lat: Optional[str] = Form(None),
                lon: Optional[str] = Form(None),
                status_text: Optional[str] = Form(alias="status", default=None),
                notes: Optional[str] = Form(None)):
    r = ui_rigs.get(rid)
    if not r:
        raise HTTPException(404, "Rig not found")
    if campaignId not in ui_campaigns:
        raise HTTPException(400, "Invalid campaignId")
    r.campaignId = campaignId
    r.name = name
    r.type = RigType(type_val)
    r.lat = float(lat) if lat else None
    r.lon = float(lon) if lon else None
    r.status = status_text
    r.notes = notes
    ui_rigs[rid] = r
    return RedirectResponse(url=f"/ui/rigs/{rid}", status_code=303)

@app.post("/ui/rigs/{rid}/delete")
def ui_delete_rig(rid: str):
    ui_rigs.pop(rid, None)
    return RedirectResponse(url="/ui/rigs", status_code=303)

# -------- Well UI --------
@app.get("/ui/wells", response_class=HTMLResponse)
def ui_list_wells():
    def camp_name(cid: str) -> str:
        c = ui_campaigns.get(cid)
        return c.name if c else "?"
    rows = "".join(
        f"<tr><td>{w.name}</td><td>{camp_name(w.campaignId)}</td>"
        f"<td><a href=\"/ui/wells/{wid}\">View</a></td></tr>"
        for wid, w in ui_wells.items()
    )
    body = f"""
    <a href="/ui/wells/new">+ New Well</a>
    <table>
      <tr><th>Name</th><th>Campaign</th><th>Actions</th></tr>
      {rows}
    </table>
    """
    return _layout("Wells", body)

@app.get("/ui/wells/new", response_class=HTMLResponse)
def ui_new_well_form(campaignId: Optional[str] = None):
    options = "".join(
        f"<option value=\"{cid}\" {'selected' if campaignId==cid else ''}>{c.name}</option>"
        for cid, c in ui_campaigns.items()
    )
    body = f"""
    <form method="post" action="/ui/wells/new">
      <label>Campaign <select name="campaignId" required>{options}</select></label><br>
      <label>Name <input name="name" required></label><br>
      <label>Status <input name="status"></label><br>
      <label>Start Date <input type="date" name="startDate"></label>
      <label>End Date <input type="date" name="endDate"></label><br>
      <label>Planned TD (m) <input type="number" step="0.01" name="plannedTdM"></label>
      <label>Actual TD (m) <input type="number" step="0.01" name="actualTdM"></label><br>
      <button type="submit">Create</button>
    </form>
    """
    return _layout("New Well", body)

@app.post("/ui/wells/new")
def ui_new_well(
    campaignId: str = Form(...),
    name: str = Form(...),
    status_text: Optional[str] = Form(alias="status", default=None),
    startDate: Optional[str] = Form(None),
    endDate: Optional[str] = Form(None),
    plannedTdM: Optional[str] = Form(None),
    actualTdM: Optional[str] = Form(None),
):
    if campaignId not in ui_campaigns:
        raise HTTPException(400, "Invalid campaignId")
    wid = str(uuid4())
    ui_wells[wid] = UIWell(
        id=wid,
        campaignId=campaignId,
        name=name,
        status=status_text,
        startDate=date.fromisoformat(startDate) if startDate else None,
        endDate=date.fromisoformat(endDate) if endDate else None,
        plannedTdM=float(plannedTdM) if plannedTdM else None,
        actualTdM=float(actualTdM) if actualTdM else None,
    )
    return RedirectResponse(url=f"/ui/wells/{wid}", status_code=303)

@app.get("/ui/wells/{wid}", response_class=HTMLResponse)
def ui_view_well(wid: str):
    w = ui_wells.get(wid)
    if not w:
        return _layout("Not found", f"<p class=\"danger\">Well {wid} not found.</p>")
    options = "".join(
        f"<option value=\"{cid}\" {'selected' if cid==w.campaignId else ''}>{c.name}</option>"
        for cid, c in ui_campaigns.items()
    )
    body = f"""
      <p><b>Name:</b> {w.name}</p>
      <p><b>Campaign:</b> {ui_campaigns.get(w.campaignId).name if ui_campaigns.get(w.campaignId) else '?'}</p>
      <p><b>Status:</b> {w.status or ''}</p>
      <p><b>Dates:</b> {w.startDate or ''} - {w.endDate or ''}</p>
      <p><b>TD (m):</b> planned {w.plannedTdM or ''} | actual {w.actualTdM or ''}</p>
      <h3>Edit</h3>
      <form method="post" action="/ui/wells/{wid}/edit">
        <label>Campaign <select name="campaignId" required>{options}</select></label><br>
        <label>Name <input name="name" value="{w.name}" required></label><br>
        <label>Status <input name="status" value="{w.status or ''}"></label><br>
        <label>Start Date <input type="date" name="startDate" value="{w.startDate or ''}"></label>
        <label>End Date <input type="date" name="endDate" value="{w.endDate or ''}"></label><br>
        <label>Planned TD (m) <input type="number" step="0.01" name="plannedTdM" value="{w.plannedTdM or ''}"></label>
        <label>Actual TD (m) <input type="number" step="0.01" name="actualTdM" value="{w.actualTdM or ''}"></label><br>
        <button type="submit">Save</button>
      </form>
      <form method="post" action="/ui/wells/{wid}/delete" onsubmit="return confirm('Delete well?')">
        <button type="submit" class="danger">Delete</button>
      </form>
    """
    return _layout(f"Well: {w.name}", body)

@app.post("/ui/wells/{wid}/edit")
def ui_edit_well(wid: str,
                 campaignId: str = Form(...),
                 name: str = Form(...),
                 status_text: Optional[str] = Form(alias="status", default=None),
                 startDate: Optional[str] = Form(None),
                 endDate: Optional[str] = Form(None),
                 plannedTdM: Optional[str] = Form(None),
                 actualTdM: Optional[str] = Form(None)):
    w = ui_wells.get(wid)
    if not w:
        raise HTTPException(404, "Well not found")
    if campaignId not in ui_campaigns:
        raise HTTPException(400, "Invalid campaignId")
    w.campaignId = campaignId
    w.name = name
    w.status = status_text
    w.startDate = date.fromisoformat(startDate) if startDate else None
    w.endDate = date.fromisoformat(endDate) if endDate else None
    w.plannedTdM = float(plannedTdM) if plannedTdM else None
    w.actualTdM = float(actualTdM) if actualTdM else None
    ui_wells[wid] = w
    return RedirectResponse(url=f"/ui/wells/{wid}", status_code=303)

@app.post("/ui/wells/{wid}/delete")
def ui_delete_well(wid: str):
    ui_wells.pop(wid, None)
    return RedirectResponse(url="/ui/wells", status_code=303)


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

    # Seed UI domain with one campaign
    if not ui_campaigns:
        seed_cid = str(uuid4())
        ui_campaigns[seed_cid] = UICampaign(id=seed_cid, name="Delta Campaign", status=RecordStatus.active)


# To run locally:
#   1) pip install -r requirements.txt
#   2) uvicorn main:app --reload
#   Or: python main.py

if __name__ == "__main__":
    # Allow running via: python main.py
    import os
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", "8000")), reload=True)
