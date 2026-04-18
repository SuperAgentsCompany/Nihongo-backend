import os
import time
from celery import Celery
import logging
from sqlalchemy import update
from .database import engine, AsyncSessionLocal
from .models import Task, TaskStatus
import asyncio
import json
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
celery_app = Celery(
    "worker",
    broker=f"redis://{REDIS_HOST}:6379/0",
    backend=f"redis://{REDIS_HOST}:6379/0"
)

# Sync Redis client for worker
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return loop.run_until_complete(coro)

async def update_task_status(task_id: str, status: TaskStatus, result: dict = None):
    async with AsyncSessionLocal() as session:
        stmt = update(Task).where(Task.id == task_id).values(status=status)
        if result:
            stmt = stmt.values(result=result)
        await session.execute(stmt)
        await session.commit()
    logger.info(f"Task {task_id} updated to {status}")
    
    # Notify via Redis Pub/Sub
    payload = {"event": "task_update", "status": status, "task_id": task_id}
    redis_client.publish(f"task_updates_{task_id}", json.dumps(payload))

def publish_event(task_id: str, event_type: str, data: dict):
    payload = {"event": event_type, "data": data, "task_id": task_id}
    redis_client.publish(f"task_updates_{task_id}", json.dumps(payload))
    logger.info(f"Published {event_type} for task {task_id}")

@celery_app.task
def run_orchestration(task_id: str):
    logger.info(f"Starting orchestration for task: {task_id}")
    
    # 1. PLANNING
    run_async(update_task_status(task_id, TaskStatus.PLANNING))
    publish_event(task_id, "agent_thought", {"agent": "Dispatcher", "text": "Analyzing task requirements..."})
    time.sleep(2)
    
    # 2. RUNNING
    run_async(update_task_status(task_id, TaskStatus.RUNNING))
    
    handoffs = [
        ("Researcher", "Searching for multi-agent swarm papers..."),
        ("Analyst", "Identifying trade-offs in decentralized orchestration..."),
        ("Synthesizer", "Drafting final architectural recommendation.")
    ]
    
    for agent, thought in handoffs:
        publish_event(task_id, "handoff", {"next_agent": agent})
        time.sleep(1)
        publish_event(task_id, "agent_thought", {"agent": agent, "text": thought})
        time.sleep(2)
        publish_event(task_id, "agent_action", {"agent": agent, "action": "Executing tool...", "tool": "web_search"})
        time.sleep(2)
    
    # 3. REVIEW
    run_async(update_task_status(task_id, TaskStatus.REVIEW))
    publish_event(task_id, "agent_thought", {"agent": "Dispatcher", "text": "Validating agent outputs..."})
    time.sleep(2)
    
    # 4. COMPLETED
    final_result = {"summary": "Orchestration successfully completed."}
    run_async(update_task_status(task_id, TaskStatus.COMPLETED, result=final_result))
    
    return {"status": "COMPLETED", "task_id": task_id}

@celery_app.task
def send_waitlist_welcome_email(email: str):
    logger.info(f"Sending welcome email to {email}")
    time.sleep(2)
    return {"status": "sent", "email": email}

@celery_app.task
def send_followup_email_1(email: str):
    time.sleep(1)
    return {"status": "sent", "email": email}

@celery_app.task
def send_followup_email_2(email: str):
    time.sleep(1)
    return {"status": "sent", "email": email}
