from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any, Dict
from .models import TaskStatus

class WaitlistRequest(BaseModel):
    email: EmailStr

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AgentBase(BaseModel):
    name: str
    role: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None

class AgentCreate(AgentBase):
    project_id: Optional[UUID] = None

class Agent(AgentBase):
    id: UUID
    project_id: UUID

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    project_id: Optional[UUID] = None

class Task(TaskBase):
    id: UUID
    project_id: UUID
    status: TaskStatus
    result: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True

class KnowledgeBaseBase(BaseModel):
    filename: str
    content: str
    metadata_json: Optional[Dict[str, Any]] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    project_id: Optional[UUID] = None

class KnowledgeBase(KnowledgeBaseBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
