from datetime import datetime, date
from typing import List, Optional
from src.models.user import UserOut, UserCreate, UserUpdate, UserRole
from src.models.campaign import CampaignOut, CampaignCreate, CampaignUpdate
from src.models.task import TaskOut, TaskCreate, TaskUpdate, TaskComment
from src.models.rig import RigOut, RigCreate, RigUpdate
from src.models.well import WellOut, WellCreate, WellUpdate
import uuid

# Mock data storage
mock_users = []
mock_campaigns = []
mock_tasks = []
mock_rigs = []
mock_wells = []


def initialize_mock_data():
    """Initialize mock data for testing"""
    global mock_users, mock_campaigns, mock_tasks, mock_rigs, mock_wells
    
    # Clear existing data
    mock_users = []
    mock_campaigns = []
    mock_tasks = []
    mock_rigs = []
    mock_wells = []
    
    # Create mock users
    user1 = UserOut(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Admin User",
        timezone="UTC",
        active=True,
        roles=[UserRole.admin],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_users.append(user1)
    
    # Create mock campaigns
    campaign1 = CampaignOut(
        id=1,
        name="Alpha-1",
        rig="Rig 7",
        spud_date=date.today(),
        target_depth=3000.0,
        current_depth=1200.0,
        progress_pct=40.0,
        days_elapsed=10,
        last_updated=datetime.utcnow()
    )
    mock_campaigns.append(campaign1)
    
    # Create mock tasks
    task1 = TaskOut(
        id=str(uuid.uuid4()),
        title="BOP Test",
        description="Perform BOP pressure test",
        status="in_progress",
        priority="normal",
        due_date=date.today(),
        assigned_to="eng1",
        campaign_id=1,
        well_id=None,
        comments=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_tasks.append(task1)
    
    # Create mock rigs
    rig1 = RigOut(
        id=str(uuid.uuid4()),
        campaign_id="1",
        name="Rig 7",
        type="jackup",
        lat=29.9383,
        lon=90.0454,
        status="Drilling",
        notes="Currently drilling Alpha-1 campaign",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_rigs.append(rig1)
    
    # Create mock wells
    well1 = WellOut(
        id=str(uuid.uuid4()),
        campaign_id="1",
        name="Well Alpha-1",
        status="Drilling",
        start_date=date.today(),
        end_date=None,
        planned_td_m=3000.0,
        actual_td_m=1200.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_wells.append(well1)


# User service mock implementations
def get_user(db, user_id: str):
    for user in mock_users:
        if user.id == user_id:
            return user
    return None


def get_user_by_email(db, email: str):
    for user in mock_users:
        if user.email == email:
            return user
    return None


def get_users(db, skip: int = 0, limit: int = 100):
    return mock_users[skip:skip+limit]


def create_user(db, user: UserCreate):
    new_user = UserOut(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
        timezone=user.timezone or "UTC",
        active=True,
        roles=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_users.append(new_user)
    return new_user


def update_user(db, user_id: str, user_update: UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    return user


def delete_user(db, user_id: str):
    user = get_user(db, user_id)
    if not user:
        return None
    
    mock_users.remove(user)
    return user


def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    # In a real implementation, we would verify the password
    # For mock purposes, we'll just check if the user exists
    return user


def get_user_roles(db, user_id: str) -> List[UserRole]:
    user = get_user(db, user_id)
    if user:
        return user.roles
    return []


def add_user_role(db, user_id: str, role: UserRole):
    user = get_user(db, user_id)
    if user and role not in user.roles:
        user.roles.append(role)
        user.updated_at = datetime.utcnow()
    return user


def remove_user_role(db, user_id: str, role: UserRole):
    user = get_user(db, user_id)
    if user and role in user.roles:
        user.roles.remove(role)
        user.updated_at = datetime.utcnow()
        return True
    return False


# Campaign service mock implementations
def get_campaign(db, campaign_id: int):
    for campaign in mock_campaigns:
        if campaign.id == campaign_id:
            return campaign
    return None


def get_campaigns(db, skip: int = 0, limit: int = 100):
    return mock_campaigns[skip:skip+limit]


def create_campaign(db, campaign: CampaignCreate):
    new_id = max([c.id for c in mock_campaigns], default=0) + 1
    new_campaign = CampaignOut(
        id=new_id,
        name=campaign.name,
        rig=campaign.rig,
        spud_date=campaign.spud_date,
        target_depth=campaign.target_depth,
        current_depth=campaign.current_depth,
        progress_pct=0.0,
        days_elapsed=0,
        last_updated=datetime.utcnow()
    )
    mock_campaigns.append(new_campaign)
    return new_campaign


def update_campaign(db, campaign_id: int, campaign_update: CampaignUpdate):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return None
    
    update_data = campaign_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)
    
    campaign.last_updated = datetime.utcnow()
    return campaign


def delete_campaign(db, campaign_id: int):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return None
    
    mock_campaigns.remove(campaign)
    return campaign


def get_campaign_progress(campaign: CampaignOut) -> float:
    if campaign.target_depth and campaign.target_depth > 0:
        return round((campaign.current_depth / campaign.target_depth) * 100, 2)
    return 0.0


def get_campaign_days_elapsed(campaign: CampaignOut) -> int:
    if campaign.spud_date:
        return (date.today() - campaign.spud_date).days
    return 0


def get_campaign_status(campaign: CampaignOut) -> str:
    if campaign.current_depth >= campaign.target_depth:
        return "Completed"
    elif campaign.current_depth > 0:
        return "In Progress"
    else:
        return "Not Started"


# Task service mock implementations
def get_task(db, task_id: str):
    for task in mock_tasks:
        if task.id == task_id:
            return task
    return None


def get_tasks(db, skip: int = 0, limit: int = 100, campaign_id: Optional[int] = None, status: Optional[str] = None):
    result = mock_tasks
    if campaign_id:
        result = [t for t in result if t.campaign_id == campaign_id]
    if status:
        result = [t for t in result if t.status == status]
    return result[skip:skip+limit]


def create_task(db, task: TaskCreate):
    new_task = TaskOut(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        campaign_id=task.campaign_id,
        well_id=task.well_id,
        comments=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_tasks.append(new_task)
    return new_task


def update_task(db, task_id: str, task_update: TaskUpdate):
    task = get_task(db, task_id)
    if not task:
        return None
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    return task


def delete_task(db, task_id: str):
    task = get_task(db, task_id)
    if not task:
        return None
    
    mock_tasks.remove(task)
    return task


def add_task_comment(db, task_id: str, comment_data):
    task = get_task(db, task_id)
    if not task:
        return None
    
    comment = TaskComment(
        author=comment_data.author,
        message=comment_data.message,
        timestamp_utc=datetime.utcnow()
    )
    task.comments.append(comment)
    task.updated_at = datetime.utcnow()
    return task


def get_task_comments(db, task_id: str):
    task = get_task(db, task_id)
    if not task:
        return []
    return task.comments


# Rig service mock implementations
def get_rig(db, rig_id: str):
    for rig in mock_rigs:
        if rig.id == rig_id:
            return rig
    return None


def get_rigs(db, skip: int = 0, limit: int = 100, campaign_id: Optional[str] = None):
    result = mock_rigs
    if campaign_id:
        result = [r for r in result if r.campaign_id == campaign_id]
    return result[skip:skip+limit]


def create_rig(db, rig: RigCreate):
    new_rig = RigOut(
        id=str(uuid.uuid4()),
        campaign_id=rig.campaign_id,
        name=rig.name,
        type=rig.type,
        lat=rig.lat,
        lon=rig.lon,
        status=rig.status,
        notes=rig.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_rigs.append(new_rig)
    return new_rig


def update_rig(db, rig_id: str, rig_update: RigUpdate):
    rig = get_rig(db, rig_id)
    if not rig:
        return None
    
    update_data = rig_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rig, key, value)
    
    rig.updated_at = datetime.utcnow()
    return rig


def delete_rig(db, rig_id: str):
    rig = get_rig(db, rig_id)
    if not rig:
        return None
    
    mock_rigs.remove(rig)
    return rig


# Well service mock implementations
def get_well(db, well_id: str):
    for well in mock_wells:
        if well.id == well_id:
            return well
    return None


def get_wells(db, skip: int = 0, limit: int = 100, campaign_id: Optional[str] = None):
    result = mock_wells
    if campaign_id:
        result = [w for w in result if w.campaign_id == campaign_id]
    return result[skip:skip+limit]


def create_well(db, well: WellCreate):
    new_well = WellOut(
        id=str(uuid.uuid4()),
        campaign_id=well.campaign_id,
        name=well.name,
        status=well.status,
        start_date=well.start_date,
        end_date=well.end_date,
        planned_td_m=well.planned_td_m,
        actual_td_m=well.actual_td_m,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_wells.append(new_well)
    return new_well


def update_well(db, well_id: str, well_update: WellUpdate):
    well = get_well(db, well_id)
    if not well:
        return None
    
    update_data = well_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(well, key, value)
    
    well.updated_at = datetime.utcnow()
    return well


def delete_well(db, well_id: str):
    well = get_well(db, well_id)
    if not well:
        return None
    
    mock_wells.remove(well)
    return well


# Initialize mock data
initialize_mock_data()