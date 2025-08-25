from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database import get_db
from src.database.models import User
from src.auth.jwt_handler import decode_access_token
from src.services.user_service import get_user
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = decode_access_token(token)
    except Exception:
        raise credentials_exception
    
    user = get_user(db, token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    """
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """
    Dependency for checking user roles.
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)):
        user_roles = [role.role for role in user.user_roles]
        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


# Role checkers for different roles
admin_required = RoleChecker(["admin"])
ops_manager_required = RoleChecker(["admin", "ops_manager"])
engineer_required = RoleChecker(["admin", "ops_manager", "engineer"])
logistics_required = RoleChecker(["admin", "logistics"])
executive_required = RoleChecker(["admin", "executive"])