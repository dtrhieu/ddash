from sqlalchemy.orm import Session
from src.database.models import Task, TaskComment
from src.models.task import TaskCreate, TaskUpdate, TaskCommentCreate
from datetime import datetime
import uuid
from typing import List, Optional


def get_task(db: Session, task_id: str):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100, campaign_id: Optional[str] = None, status: Optional[str] = None):
    query = db.query(Task)
    if campaign_id:
        query = query.filter(Task.campaign_id == campaign_id)
    if status:
        query = query.filter(Task.status == status)
    return query.offset(skip).limit(limit).all()


def create_task(db: Session, task: TaskCreate):
    db_task = Task(
        id=str(uuid.uuid4()),
        campaign_id=task.campaign_id,
        well_id=task.well_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assignee_id=task.assignee_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: str, task_update: TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: str):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db.delete(db_task)
    db.commit()
    return db_task


def add_task_comment(db: Session, task_id: str, comment: TaskCommentCreate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_comment = TaskComment(
        id=str(uuid.uuid4()),
        task_id=task_id,
        author_id=comment.author,
        body=comment.message
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_task_comments(db: Session, task_id: str):
    return db.query(TaskComment).filter(TaskComment.task_id == task_id).all()