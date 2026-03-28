"""
FastAPI server for OpenEnv Email Triage Environment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os

from environment import EmailTriageEnv, Action

app = FastAPI(title="Email Triage OpenEnv")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = EmailTriageEnv()

class StepRequest(BaseModel):
    action: Dict[str, Any]

@app.get("/")
async def root():
    return {
        "openenv": {
            "name": "Email Triage Environment",
            "description": "Real-world email management simulation for AI agents",
            "version": "1.0.0",
            "endpoints": {
                "reset": "/reset",
                "step": "/step",
                "state": "/state",
                "grader": "/grader",
                "tasks": "/tasks"
            }
        }
    }

@app.post("/reset")
async def reset(task_id: int = 1):
    try:
        observation = env.reset(task_id=task_id)
        return {
            "observation": {
                "visible_emails": observation.visible_emails,
                "task_description": observation.task_description,
                "actions_taken": observation.actions_taken,
                "max_actions": observation.max_actions,
                "current_score": observation.current_score,
                "task_id": observation.task_id
            },
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
async def step(request: StepRequest):
    try:
        action = Action(
            action_type=request.action["action_type"],
            email_id=request.action["email_id"],
            reply_content=request.action.get("reply_content"),
            new_priority=request.action.get("new_priority")
        )
        
        observation, reward, done, info = env.step(action)
        
        return {
            "observation": {
                "visible_emails": observation.visible_emails,
                "task_description": observation.task_description,
                "actions_taken": observation.actions_taken,
                "max_actions": observation.max_actions,
                "current_score": observation.current_score,
                "task_id": observation.task_id
            },
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    return env.state()

@app.get("/grader")
async def get_grade():
    return {"grade": env.grade(), "task_id": env.task_id}

@app.get("/tasks")
async def list_tasks():
    return {
        "tasks": [
            {"id": 1, "name": "Easy - Simple Email Filtering", "difficulty": "easy", "max_actions": 10},
            {"id": 2, "name": "Medium - Priority Management", "difficulty": "medium", "max_actions": 20},
            {"id": 3, "name": "Hard - Complex Workflow", "difficulty": "hard", "max_actions": 25}
        ]
    }
