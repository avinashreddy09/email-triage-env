from pydantic import BaseModel
from typing import Literal, Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Email(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    priority: Priority = Priority.NORMAL
    is_read: bool = False
    is_archived: bool = False
    is_spam: bool = False
    timestamp: datetime = datetime.now()
    
class Action(BaseModel):
    action_type: Literal["reply", "archive", "delete", "mark_spam", "mark_read", "prioritize"]
    email_id: int
    reply_content: Optional[str] = None
    new_priority: Optional[Priority] = None
    
class Observation(BaseModel):
    visible_emails: List[Email]
    current_task_description: str
    actions_taken_so_far: int
    max_actions: int
    current_score: float
    task_id: int
