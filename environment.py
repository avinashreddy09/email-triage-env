"""OpenEnv-compliant Email Triage Environment with Pydantic models"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Email(BaseModel):
    """Email data model"""
    id: int
    sender: str
    subject: str
    body: str
    priority: Priority = Priority.NORMAL
    is_read: bool = False
    is_archived: bool = False
    is_spam: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class Action(BaseModel):
    """Action data model"""
    action_type: str  # reply, archive, delete, mark_spam, mark_read, prioritize
    email_id: int
    reply_content: Optional[str] = None
    new_priority: Optional[Priority] = None

class Observation(BaseModel):
    """Observation data model"""
    visible_emails: List[Dict[str, Any]]
    task_description: str
    actions_taken: int
    max_actions: int
    current_score: float
    task_id: int

class EmailTriageEnv:
    """Email Triage Environment for AI Agents"""
    
    def __init__(self):
        self.emails: List[Email] = []
        self.task_id: int = 1
        self.task_description: str = ""
        self.actions_taken: int = 0
        self.max_actions: int = 10
        self.total_reward: float = 0.0
        self.done: bool = False
        self.required_actions: List[Dict] = []
        
    def reset(self, task_id: int = 1) -> Observation:
        """Reset environment to initial state"""
        self.task_id = task_id
        self.actions_taken = 0
        self.total_reward = 0.0
        self.done = False
        
        if task_id == 1:
            self.emails = [
                Email(id=1, sender="spam@unknown.com", subject="WINNER!", body="You won $1,000,000!", is_spam=True),
                Email(id=2, sender="customer@example.com", subject="Product Question", body="Can you tell me about pricing?"),
                Email(id=3, sender="newsletter@company.com", subject="Newsletter", body="Weekly updates")
            ]
            self.task_description = "Easy: Archive spam email and reply to customer inquiry"
            self.max_actions = 10
            self.required_actions = [
                {"action": "mark_spam", "email_id": 1},
                {"action": "reply", "email_id": 2}
            ]
        elif task_id == 2:
            self.emails = [
                Email(id=1, sender="ceo@company.com", subject="URGENT: Board Meeting", body="Meeting in 1 hour", priority=Priority.URGENT),
                Email(id=2, sender="client@bigcorp.com", subject="Contract Review", body="Review by EOD", priority=Priority.HIGH),
                Email(id=3, sender="spammer@fake.com", subject="Buy Watches", body="Cheap watches!", is_spam=True),
                Email(id=4, sender="colleague@company.com", subject="Lunch?", body="Want to grab lunch?", priority=Priority.LOW),
                Email(id=5, sender="newsletter@tech.com", subject="Tech News", body="Latest tech updates", priority=Priority.LOW),
                Email(id=6, sender="newsletter@marketing.com", subject="Marketing Tips", body="10 strategies", priority=Priority.LOW),
                Email(id=7, sender="support@company.com", subject="Customer Complaint", body="Product defective", priority=Priority.HIGH),
                Email(id=8, sender="meeting@calendar.com", subject="Schedule Meeting", body="Propose times", priority=Priority.NORMAL)
            ]
            self.task_description = "Medium: Handle urgent emails, mark spam, archive newsletters"
            self.max_actions = 20
            self.required_actions = [
                {"action": "reply", "email_id": 1},
                {"action": "mark_spam", "email_id": 3},
                {"action": "archive", "email_id": 4},
                {"action": "archive", "email_id": 5},
                {"action": "archive", "email_id": 6},
                {"action": "reply", "email_id": 8}
            ]
        else:
            self.emails = [
                Email(id=1, sender="angry_customer@gmail.com", subject="COMPLAINT", body="Product broken, want refund!", priority=Priority.URGENT),
                Email(id=2, sender="escalation@manager.com", subject="URGENT: Escalation", body="Client threatening to leave", priority=Priority.URGENT),
                Email(id=3, sender="partner@vendor.com", subject="Partnership", body="Discuss partnership opportunity", priority=Priority.HIGH),
                Email(id=4, sender="phishing@fakebank.com", subject="Account Compromised", body="Click here to verify", is_spam=True),
                Email(id=5, sender="colleague@team.com", subject="Project Update", body="Need status update", priority=Priority.HIGH),
                Email(id=6, sender="spam@advertising.com", subject="Make Money", body="Work from home", is_spam=True),
                Email(id=7, sender="customer@support.com", subject="Follow-up", body="Following up on previous inquiry", priority=Priority.NORMAL),
                Email(id=8, sender="newsletter@industry.com", subject="Weekly Digest", body="Industry news", priority=Priority.LOW)
            ]
            self.task_description = "Hard: Handle complaints, escalations, multiple priorities"
            self.max_actions = 25
            self.required_actions = [
                {"action": "reply", "email_id": 1},
                {"action": "reply", "email_id": 2},
                {"action": "reply", "email_id": 3},
                {"action": "mark_spam", "email_id": 4},
                {"action": "reply", "email_id": 5},
                {"action": "mark_spam", "email_id": 6},
                {"action": "reply", "email_id": 7},
                {"action": "archive", "email_id": 8}
            ]
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        """Execute an action"""
        if self.done:
            return self._get_observation(), 0.0, True, {"error": "Episode already done"}
        
        email = next((e for e in self.emails if e.id == action.email_id), None)
        if not email:
            return self._get_observation(), -0.5, False, {"error": f"Email {action.email_id} not found"}
        
        reward = 0.0
        info = {"action": action.action_type}
        
        if action.action_type == "mark_spam":
            if not email.is_spam:
                email.is_spam = True
                email.is_archived = True
                reward = 0.8
                info["reason"] = f"Marked spam from {email.sender}"
            else:
                reward = -0.2
                info["reason"] = "Already spam"
        elif action.action_type == "reply":
            if action.reply_content:
                email.is_read = True
                reward = 0.5
                info["reason"] = f"Replied to {email.sender}"
            else:
                reward = -0.2
                info["reason"] = "No content"
        elif action.action_type == "archive":
            if not email.is_archived:
                email.is_archived = True
                reward = 0.2
                info["reason"] = f"Archived email {email.id}"
            else:
                reward = -0.1
                info["reason"] = "Already archived"
        
        self.actions_taken += 1
        self.total_reward += reward
        
        if self._is_task_complete():
            self.done = True
            reward += 2.0
            info["task_complete"] = True
        
        if self.actions_taken >= self.max_actions:
            self.done = True
        
        return self._get_observation(), reward, self.done, info
    
    def state(self) -> Dict[str, Any]:
        """Return current internal state"""
        return {
            "task_id": self.task_id,
            "actions_taken": self.actions_taken,
            "max_actions": self.max_actions,
            "total_reward": self.total_reward,
            "done": self.done
        }
    
    def grade(self) -> float:
        """Return final grade 0.0-1.0"""
        if not self.required_actions:
            return 1.0
        
        completed = 0
        for req in self.required_actions:
            email = next((e for e in self.emails if e.id == req["email_id"]), None)
            if not email:
                continue
            if req["action"] == "mark_spam" and email.is_spam:
                completed += 1
            elif req["action"] == "archive" and email.is_archived:
                completed += 1
            elif req["action"] == "reply" and email.is_read:
                completed += 1
        
        return completed / len(self.required_actions)
    
    def _get_observation(self) -> Observation:
        """Create observation"""
        visible = [
            {
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "body": e.body[:200],
                "priority": e.priority.value,
                "is_read": e.is_read
            }
            for e in self.emails if not e.is_archived
        ]
        return Observation(
            visible_emails=visible,
            task_description=self.task_description,
            actions_taken=self.actions_taken,
            max_actions=self.max_actions,
            current_score=self.total_reward,
            task_id=self.task_id
        )
    
    def _is_task_complete(self) -> bool:
        """Check if all required actions are done"""
        for req in self.required_actions:
            email = next((e for e in self.emails if e.id == req["email_id"]), None)
            if not email:
                return False
            if req["action"] == "mark_spam" and not email.is_spam:
                return False
            if req["action"] == "archive" and not email.is_archived:
                return False
            if req["action"] == "reply" and not email.is_read:
                return False
        return True
