from fastapi import APIRouter, HTTPException, status
from src.models.user import UserCreate, UserOut, UserUpdate, UserLogin, Token
from src.services.mock_services import create_user, get_user, get_users, update_user, delete_user, authenticate_user, add_user_role
from src.auth import create_access_token
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate):
    # For mock implementation, we don't actually use a database session
    # We pass None as the db parameter to maintain compatibility with the service interface
    db_user = create_user(None, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User could not be created")
    return db_user


@router.get("/", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 100):
    # For mock implementation, we don't actually use a database session
    users = get_users(None, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: str):
    # For mock implementation, we don't actually use a database session
    db_user = get_user(None, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserOut)
def update_existing_user(user_id: str, user_update: UserUpdate):
    # For mock implementation, we don't actually use a database session
    db_user = update_user(None, user_id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(user_id: str):
    # For mock implementation, we don't actually use a database session
    db_user = delete_user(None, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return


@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin):
    # For mock implementation, we don't actually use a database session
    user = authenticate_user(None, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}