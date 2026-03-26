"""FastAPI server for Hugging Face deployment"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import subprocess
import os

from environment import EmailTriageEnv, Action, Observation

app = FastAPI(title="Email Triage OpenEnv", description="Real-world email management environment")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = EmailTriageEnv()

class StepRequest(BaseModel):
    action: Dict[str, Any]

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]

class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    task_id: int

@app.get("/")
async def root():
    return {
        "name": "Email Triage OpenEnv",
        "version": "1.0.0",
        "description": "Real-world email management simulation for AI agents",
        "endpoints": [
            "GET / - This info",
            "POST /reset - Reset environment with task_id",
            "POST /step - Take an action",
            "GET /state - Get current state",
            "GET /baseline - Run baseline inference",
            "GET /grader - Get final grade",
            "GET /tasks - List tasks and action schema"
        ]
    }

@app.post("/reset", response_model=ResetResponse)
async def reset(task_id: int = 1):
    """Reset environment to start a task (1=easy, 2=medium, 3=hard)"""
    try:
        observation = env.reset(task_id=task_id)
        return ResetResponse(
            observation={
                "visible_emails": observation.visible_emails,
                "task_description": observation.task_description,
                "actions_taken": observation.actions_taken,
                "max_actions": observation.max_actions,
                "current_score": observation.current_score,
                "task_id": observation.task_id
            },
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest):
    """Take an action in the environment"""
    try:
        # Convert dict to Action object
        action = Action(
            action_type=request.action["action_type"],
            email_id=request.action["email_id"],
            reply_content=request.action.get("reply_content"),
            new_priority=request.action.get("new_priority")
        )
        
        observation, reward, done, info = env.step(action)
        
        return StepResponse(
            observation={
                "visible_emails": observation.visible_emails,
                "task_description": observation.task_description,
                "actions_taken": observation.actions_taken,
                "max_actions": observation.max_actions,
                "current_score": observation.current_score,
                "task_id": observation.task_id
            },
            reward=reward,
            done=done,
            info=info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    """Get current environment state"""
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/grader")
async def get_grade():
    """Get final grade for current episode (0.0-1.0)"""
    try:
        grade = env.grade()
        return {"grade": grade, "task_id": env.task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks")
async def list_tasks():
    """List all available tasks and action schema"""
    return {
        "tasks": [
            {
                "id": 1,
                "name": "Easy - Simple Email Filtering",
                "description": "Archive spam and reply to customer inquiry",
                "difficulty": "easy",
                "max_actions": 10,
                "success_criteria": "Mark spam email and reply to customer"
            },
            {
                "id": 2,
                "name": "Medium - Priority Management",
                "description": "Handle urgent emails and manage priorities",
                "difficulty": "medium",
                "max_actions": 20,
                "success_criteria": "Reply to urgent emails, mark spam, archive newsletters"
            },
            {
                "id": 3,
                "name": "Hard - Complex Workflow",
                "description": "Handle complaints, escalations, and multiple priorities",
                "difficulty": "hard",
                "max_actions": 25,
                "success_criteria": "Handle all complaints, escalations, and routine emails"
            }
        ],
        "action_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["reply", "archive", "delete", "mark_spam", "mark_read", "prioritize"],
                    "description": "Type of action to perform"
                },
                "email_id": {
                    "type": "integer",
                    "description": "ID of the email to act on"
                },
                "reply_content": {
                    "type": "string",
                    "description": "Content for reply action (required for reply)"
                },
                "new_priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"],
                    "description": "New priority for prioritize action"
                }
            },
            "required": ["action_type", "email_id"]
        }
    }

@app.get("/baseline")
async def run_baseline():
    """Run baseline inference script and return scores"""
    try:
        # Run baseline.py as subprocess
        result = subprocess.run(
            ["python", "baseline.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse the output to extract scores
        output = result.stdout
        error = result.stderr
        
        # Extract grades from output
        import re
        grades = re.findall(r"Grade = (\d+\.\d+)/1\.0", output)
        
        return {
            "success": result.returncode == 0,
            "output": output[-2000:],  # Last 2000 chars
            "error": error if error else None,
            "grades": [float(g) for g in grades] if grades else [],
            "average_grade": sum([float(g) for g in grades]) / len(grades) if grades else 0
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Baseline script timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Change to 127.0.0.1 for local testing
    uvicorn.run(app, host="127.0.0.1", port=7860)
