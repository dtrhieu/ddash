from fastapi import APIRouter, HTTPException, status
from src.models.task import TaskCreate, TaskOut, TaskUpdate, TaskCommentCreate
from src.services.mock_services import create_task, get_task, get_tasks, update_task, delete_task, add_task_comment, get_task_comments
from typing import List, Optional

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate):
    # For mock implementation, we don't actually use a database session
    db_task = create_task(None, task)
    if not db_task:
        raise HTTPException(status_code=400, detail="Task could not be created")
    return db_task


@router.get("/", response_model=List[TaskOut])
def read_tasks(
    skip: int = 0, 
    limit: int = 100, 
    campaign_id: Optional[int] = None, 
    status: Optional[str] = None
):
    # For mock implementation, we don't actually use a database session
    tasks = get_tasks(None, skip=skip, limit=limit, campaign_id=campaign_id, status=status)
    return tasks


@router.get("/{task_id}", response_model=TaskOut)
def read_task(task_id: str):
    # For mock implementation, we don't actually use a database session
    db_task = get_task(None, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskOut)
def update_existing_task(task_id: str, task_update: TaskUpdate):
    # For mock implementation, we don't actually use a database session
    db_task = update_task(None, task_id, task_update)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: str):
    # For mock implementation, we don't actually use a database session
    db_task = delete_task(None, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return


@router.post("/{task_id}/comments", response_model=TaskOut)
def add_comment_to_task(task_id: str, comment: TaskCommentCreate):
    # For mock implementation, we don't actually use a database session
    db_comment = add_task_comment(None, task_id, comment)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_comment


@router.get("/{task_id}/comments", response_model=List[TaskCommentCreate])
def get_task_comments_list(task_id: str):
    # For mock implementation, we don't actually use a database session
    comments = get_task_comments(None, task_id)
    return comments