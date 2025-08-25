from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.task import TaskCreate, TaskOut, TaskUpdate, TaskCommentCreate
from src.services.task_service import create_task, get_task, get_tasks, update_task, delete_task, add_task_comment, get_task_comments
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = create_task(db, task)
    if not db_task:
        raise HTTPException(status_code=400, detail="Task could not be created")
    return db_task


@router.get("/", response_model=List[TaskOut])
def read_tasks(
    skip: int = 0, 
    limit: int = 100, 
    campaign_id: str = None, 
    status: str = None,
    db: Session = Depends(get_db)
):
    tasks = get_tasks(db, skip=skip, limit=limit, campaign_id=campaign_id, status=status)
    return tasks


@router.get("/{task_id}", response_model=TaskOut)
def read_task(task_id: str, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskOut)
def update_existing_task(task_id: str, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = update_task(db, task_id, task_update)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: str, db: Session = Depends(get_db)):
    db_task = delete_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return


@router.post("/{task_id}/comments", response_model=TaskOut)
def add_comment_to_task(task_id: str, comment: TaskCommentCreate, db: Session = Depends(get_db)):
    db_comment = add_task_comment(db, task_id, comment)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_comment


@router.get("/{task_id}/comments", response_model=List[TaskCommentCreate])
def get_task_comments_list(task_id: str, db: Session = Depends(get_db)):
    comments = get_task_comments(db, task_id)
    return comments