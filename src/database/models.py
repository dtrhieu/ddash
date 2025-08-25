from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
from .connection import Base
from src.models import TaskStatus, RigType, RecordStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_roles = relationship("UserRoleModel", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assignee")
    comments = relationship("TaskComment", back_populates="author")


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(UserRole), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="user_roles")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    block = Column(String, nullable=True)
    field = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(Enum(RecordStatus), default=RecordStatus.active)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rigs = relationship("Rig", back_populates="campaign", cascade="all, delete-orphan")
    wells = relationship("Well", back_populates="campaign", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="campaign", cascade="all, delete-orphan")


class Rig(Base):
    __tablename__ = "rigs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(RigType), nullable=False)
    lat = Column(Numeric(precision=9, scale=6), nullable=True)
    lon = Column(Numeric(precision=9, scale=6), nullable=True)
    status = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="rigs")


class Well(Base):
    __tablename__ = "wells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    planned_td_m = Column(Numeric(precision=12, scale=2), nullable=True)
    actual_td_m = Column(Numeric(precision=12, scale=2), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="wells")
    tasks = relationship("Task", back_populates="well", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    well_id = Column(UUID(as_uuid=True), ForeignKey("wells.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.backlog)
    priority = Column(String, nullable=True)
    labels = Column(ARRAY(String), nullable=True)
    due_date = Column(Date, nullable=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="tasks")
    well = relationship("Well", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_type = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    s3_key = Column(String, nullable=False)
    sha256 = Column(String, nullable=True)
    uploaded_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String, nullable=True)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    before = Column(Text, nullable=True)
    after = Column(Text, nullable=True)
    at = Column(DateTime, default=datetime.utcnow)