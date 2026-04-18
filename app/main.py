from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from .database import engine, Base, get_db
from .models import Waitlist, Project, Agent, Task, TaskStatus, KnowledgeBase
from .schemas import WaitlistRequest, ProjectCreate, Project as ProjectSchema, AgentCreate, Agent as AgentSchema, TaskCreate, Task as TaskSchema, KnowledgeBaseCreate, KnowledgeBase as KnowledgeBaseSchema
from .worker import send_waitlist_welcome_email, send_followup_email_1, send_followup_email_2
from .auth import create_access_token, get_current_user
from pydantic import EmailStr
from typing import List, Dict
import logging
import uuid
import asyncio
import os
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SUPAA API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "superagents")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "superagents")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

@app.get("/")
async def root():
    return {"message": "Welcome to SUPAA API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast(self, message: str, task_id: str):
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/orchestration/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    # Note: WebSocket auth can be tricky, for prototype we'll skip token check for now 
    # or use a query param. For now let's just accept.
    await manager.connect(websocket, task_id)
    
    # Listen to Redis Pub/Sub for this task_id
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    pubsub = r.pubsub()
    await pubsub.subscribe(f"task_updates_{task_id}")
    
    try:
        # Create a task to listen for Redis messages and broadcast them
        async def listen_to_redis():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"].decode("utf-8"))

        # Run the listener in the background
        listener_task = asyncio.create_task(listen_to_redis())
        
        # Keep the connection open and wait for client to disconnect
        while True:
            await websocket.receive_text() # Just to keep alive/detect disconnect
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
        await pubsub.unsubscribe(f"task_updates_{task_id}")
        listener_task.cancel()

# --- Waitlist (Public) ---
@app.post("/waitlist")
async def join_waitlist(request: WaitlistRequest, db: AsyncSession = Depends(get_db)):
    query = select(Waitlist).where(Waitlist.email == request.email)
    result = await db.execute(query)
    existing_entry = result.scalars().first()
    if existing_entry:
        return {"message": "You've already joined the waitlist!", "email": request.email}
    new_entry = Waitlist(email=request.email)
    db.add(new_entry)
    try:
        await db.commit()
        send_waitlist_welcome_email.delay(request.email)
        send_followup_email_1.apply_async(args=[request.email], countdown=259200)
        send_followup_email_2.apply_async(args=[request.email], countdown=604800)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return {"message": "Successfully joined the waitlist", "email": request.email}

# --- Projects (Protected) ---
@app.get("/projects", response_model=List[ProjectSchema])
async def list_projects(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Project)
    result = await db.execute(query)
    return result.scalars().all()

@app.post("/projects", response_model=ProjectSchema)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    new_project = Project(name=project.name, description=project.description)
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@app.get("/projects/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# --- Agents (Protected) ---
@app.get("/agents", response_model=List[AgentSchema])
async def list_agents(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Agent)
    result = await db.execute(query)
    return result.scalars().all()

@app.post("/projects/{project_id}/agents", response_model=AgentSchema)
async def create_agent(project_id: uuid.UUID, agent: AgentCreate, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    new_agent = Agent(project_id=project_id, name=agent.name, role=agent.role, system_prompt=agent.system_prompt, model=agent.model)
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    return new_agent

@app.get("/projects/{project_id}/agents", response_model=List[AgentSchema])
async def list_project_agents(project_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Agent).where(Agent.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()

# --- Tasks (Protected) ---
@app.post("/projects/{project_id}/tasks", response_model=TaskSchema)
async def create_task(project_id: uuid.UUID, task: TaskCreate, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    new_task = Task(project_id=project_id, title=task.title, description=task.description, status=TaskStatus.PENDING)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    from .worker import run_orchestration
    run_orchestration.delay(str(new_task.id))
    return new_task

@app.get("/projects/{project_id}/tasks", response_model=List[TaskSchema])
async def list_project_tasks(project_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Task).where(Task.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()

@app.get("/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# --- Knowledge Base (Protected) ---
@app.post("/projects/{project_id}/knowledge", response_model=KnowledgeBaseSchema)
async def create_knowledge(project_id: uuid.UUID, knowledge: KnowledgeBaseCreate, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Note: In a real implementation, we would generate the embedding here
    # For now, we'll use a dummy vector or leave it null
    new_knowledge = KnowledgeBase(
        project_id=project_id,
        filename=knowledge.filename,
        content=knowledge.content,
        metadata_json=knowledge.metadata_json
    )
    db.add(new_knowledge)
    await db.commit()
    await db.refresh(new_knowledge)
    return new_knowledge

@app.get("/projects/{project_id}/knowledge", response_model=List[KnowledgeBaseSchema])
async def list_project_knowledge(project_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()
