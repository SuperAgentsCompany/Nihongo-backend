import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
import asyncio
import uuid

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def auth_headers(client):
    # Use default credentials defined in main.py
    response = client.post("/token", data={"username": "superagents", "password": "superagents"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SUPAA API"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_join_waitlist(client):
    email = "test@example.com"
    response = client.post("/waitlist", json={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully joined the waitlist"
    assert response.json()["email"] == email

    # Test joining again
    response = client.post("/waitlist", json={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == "You've already joined the waitlist!"

def test_login(client):
    response = client.post("/token", data={"username": "superagents", "password": "superagents"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    response = client.post("/token", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401

def test_project_lifecycle(client, auth_headers):
    # Create project
    response = client.post("/projects", json={"name": "Test Project", "description": "Test Desc"}, headers=auth_headers)
    assert response.status_code == 200
    project_id = response.json()["id"]
    assert response.json()["name"] == "Test Project"

    # List projects
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == project_id

    # Get project
    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_agent_lifecycle(client, auth_headers):
    # Create project first
    response = client.post("/projects", json={"name": "Test Project"}, headers=auth_headers)
    project_id = response.json()["id"]

    # Create agent
    response = client.post(f"/projects/{project_id}/agents", json={
        "name": "Test Agent",
        "role": "Researcher",
        "model": "gemini-1.5-pro"
    }, headers=auth_headers)
    assert response.status_code == 200
    agent_id = response.json()["id"]
    assert response.json()["name"] == "Test Agent"

    # List project agents
    response = client.get(f"/projects/{project_id}/agents", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == agent_id

def test_task_lifecycle(client, auth_headers):
    # Create project first
    response = client.post("/projects", json={"name": "Test Project"}, headers=auth_headers)
    project_id = response.json()["id"]

    # Create task
    response = client.post(f"/projects/{project_id}/tasks", json={
        "title": "Test Task",
        "description": "Task Description"
    }, headers=auth_headers)
    assert response.status_code == 200
    task_id = response.json()["id"]
    assert response.json()["title"] == "Test Task"
    assert response.json()["status"] == "PENDING"

    # Get task
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_knowledge_base_lifecycle(client, auth_headers):
    # Create project first
    response = client.post("/projects", json={"name": "Test Project"}, headers=auth_headers)
    project_id = response.json()["id"]

    # Create knowledge entry
    response = client.post(f"/projects/{project_id}/knowledge", json={
        "filename": "manual.pdf",
        "content": "This is the content of the manual."
    }, headers=auth_headers)
    assert response.status_code == 200
    knowledge_id = response.json()["id"]
    assert response.json()["filename"] == "manual.pdf"

    # List project knowledge
    response = client.get(f"/projects/{project_id}/knowledge", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == knowledge_id
