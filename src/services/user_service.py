from sqlalchemy.orm import Session
from src.database.models import User, UserRoleModel
from src.models.user import UserCreate, UserUpdate, UserRole
from passlib.context import CryptContext
import uuid
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
        timezone=user.timezone,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add default role if provided
    if hasattr(user, 'role') and user.role:
        user_role = UserRoleModel(user_id=db_user.id, role=user.role)
        db.add(user_role)
        db.commit()
    
    return db_user


def update_user(db: Session, user_id: str, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user_roles(db: Session, user_id: str) -> List[UserRole]:
    user_roles = db.query(UserRoleModel).filter(UserRoleModel.user_id == user_id).all()
    return [ur.role for ur in user_roles]


def add_user_role(db: Session, user_id: str, role: UserRole):
    user_role = UserRoleModel(user_id=user_id, role=role)
    db.add(user_role)
    db.commit()
    return user_role


def remove_user_role(db: Session, user_id: str, role: UserRole):
    user_role = db.query(UserRoleModel).filter(
        UserRoleModel.user_id == user_id,
        UserRoleModel.role == role
    ).first()
    
    if user_role:
        db.delete(user_role)
        db.commit()
        return True
    return False