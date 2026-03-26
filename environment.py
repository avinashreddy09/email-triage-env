"""
OpenEnv-compliant Email Triage Environment
Implements reset(), step(), and state() methods
"""

from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Email:
    """Email data model"""
    id: int
    sender: str
    subject: str
    body: str
    priority: str = "normal"
    is_read: bool = False
    is_archived: bool = False
    is_spam: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Action:
    """Action data model"""
    action_type: str  # reply, archive, delete, mark_spam, mark_read, prioritize
    email_id: int
    reply_content: Optional[str] = None
    new_priority: Optional[str] = None

@dataclass
class Observation:
    """Observation data model"""
    visible_emails: List[Dict]
    task_description: str
    actions_taken: int
    max_actions: int
    current_score: float
    task_id: int

class EmailTriageEnv:
    """Email Triage Environment for AI Agents"""
    
    def __init__(self):
        self.reset()
    
    def reset(self, task_id: int = 1) -> Observation:
        """Reset environment to initial state"""
        self.task_id = task_id
        self.actions_taken = 0
        self.total_reward = 0.0
        self.done = False
        
        # Define tasks
        if task_id == 1:
            # Task 1: Easy - 3 emails
            self.emails = [
                Email(1, "spam@unknown.com", "WINNER!", "You won $1,000,000!", is_spam=True),
                Email(2, "customer@example.com", "Product Question", "Can you tell me about pricing?"),
                Email(3, "newsletter@company.com", "Newsletter", "Weekly updates")
            ]
            self.task_description = "Easy: Archive spam email and reply to customer inquiry"
            self.max_actions = 10
            self.required_actions = [
                {"action": "mark_spam", "email_id": 1},
                {"action": "reply", "email_id": 2}
            ]
            
        elif task_id == 2:
            # Task 2: Medium - 8 emails with priorities
            self.emails = [
                Email(1, "ceo@company.com", "URGENT: Board Meeting", "Meeting in 1 hour", "urgent"),
                Email(2, "client@bigcorp.com", "Contract Review", "Review by EOD", "high"),
                Email(3, "spammer@fake.com", "Buy Watches", "Cheap watches!", is_spam=True),
                Email(4, "colleague@company.com", "Lunch?", "Want to grab lunch?", "low"),
                Email(5, "newsletter@tech.com", "Tech News", "Latest tech updates", "low"),
                Email(6, "newsletter@marketing.com", "Marketing Tips", "10 strategies", "low"),
                Email(7, "support@company.com", "Customer Complaint", "Product defective", "high"),
                Email(8, "meeting@calendar.com", "Schedule Meeting", "Propose times", "normal")
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
            
        else:  # task_id == 3
            # Task 3: Hard - Complex workflow
            self.emails = [
                Email(1, "angry_customer@gmail.com", "COMPLAINT", "Product broken, want refund!", "urgent"),
                Email(2, "escalation@manager.com", "URGENT: Escalation", "Client threatening to leave", "urgent"),
                Email(3, "partner@vendor.com", "Partnership", "Discuss partnership opportunity", "high"),
                Email(4, "phishing@fakebank.com", "Account Compromised", "Click here to verify", is_spam=True),
                Email(5, "colleague@team.com", "Project Update", "Need status update", "high"),
                Email(6, "spam@advertising.com", "Make Money", "Work from home", is_spam=True),
                Email(7, "customer@support.com", "Follow-up", "Following up on previous inquiry", "normal"),
                Email(8, "newsletter@industry.com", "Weekly Digest", "Industry news", "low")
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
        """Execute an action and return (observation, reward, done, info)"""
        if self.done:
            return self._get_observation(), 0.0, True, {"error": "Episode already done"}
        
        # Find the email
        email = next((e for e in self.emails if e.id == action.email_id), None)
        if not email:
            return self._get_observation(), -0.5, False, {"error": f"Email {action.email_id} not found"}
        
        reward = 0.0
        info = {"action": action.action_type, "email_id": action.email_id}
        
        # Process action and calculate reward
        if action.action_type == "mark_spam":
            if not email.is_spam:
                email.is_spam = True
                email.is_archived = True
                reward = 0.8
                info["reason"] = f"Marked spam from {email.sender}"
            else:
                reward = -0.2
                info["reason"] = "Already marked as spam"
                
        elif action.action_type == "reply":
            if action.reply_content and len(action.reply_content) > 0:
                email.is_read = True
                reward = 0.5
                info["reason"] = f"Replied to {email.sender}"
            else:
                reward = -0.2
                info["reason"] = "Reply without content"
                
        elif action.action_type == "archive":
            if not email.is_archived:
                email.is_archived = True
                reward = 0.2
                info["reason"] = f"Archived email {email.id}"
            else:
                reward = -0.1
                info["reason"] = "Already archived"
                
        elif action.action_type == "delete":
            if not email.is_archived:
                email.is_archived = True
                reward = 0.3
                info["reason"] = f"Deleted email {email.id}"
            else:
                reward = -0.1
                info["reason"] = "Already deleted"
                
        elif action.action_type == "mark_read":
            if not email.is_read:
                email.is_read = True
                reward = 0.1
                info["reason"] = f"Marked email {email.id} as read"
                
        elif action.action_type == "prioritize":
            if action.new_priority:
                old = email.priority
                email.priority = action.new_priority
                reward = 0.2 if old != action.new_priority else 0.0
                info["reason"] = f"Priority changed to {action.new_priority}"
            else:
                reward = -0.1
                info["reason"] = "Prioritize without new priority"
        
        # Update state
        self.actions_taken += 1
        self.total_reward += reward
        
        # Check if task is complete
        if self._is_task_complete():
            self.done = True
            reward += 2.0
            info["reason"] = info.get("reason", "") + " | TASK COMPLETE! +2 bonus"
            info["task_complete"] = True
        
        # Check max actions
        if self.actions_taken >= self.max_actions:
            self.done = True
            info["reason"] = info.get("reason", "") + f" | Max actions ({self.max_actions}) reached"
        
        return self._get_observation(), reward, self.done, info
    
    def state(self) -> Dict[str, Any]:
        """Return current internal state"""
        return {
            "task_id": self.task_id,
            "actions_taken": self.actions_taken,
            "max_actions": self.max_actions,
            "total_reward": self.total_reward,
            "done": self.done,
            "emails": [
                {
                    "id": e.id,
                    "sender": e.sender,
                    "subject": e.subject,
                    "priority": e.priority,
                    "is_read": e.is_read,
                    "is_archived": e.is_archived,
                    "is_spam": e.is_spam
                }
                for e in self.emails
            ]
        }
    
    def grade(self) -> float:
        """Return final grade (0.0-1.0)"""
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
        """Create observation from current state"""
        visible_emails = [
            {
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "body": e.body[:200],  # Truncate long bodies
                "priority": e.priority,
                "is_read": e.is_read
            }
            for e in self.emails if not e.is_archived
        ]
        
        return Observation(
            visible_emails=visible_emails,
            task_description=self.task_description,
            actions_taken=self.actions_taken,
            max_actions=self.max_actions,
            current_score=self.total_reward,
            task_id=self.task_id
        )
    
    def _is_task_complete(self) -> bool:
        """Check if all required actions are completed"""
        for req in self.required_actions:
            email = next((e for e in self.emails if e.id == req["email_id"]), None)
            if not email:
                return False
            
            if req["action"] == "mark_spam" and not email.is_spam:
                return False
            elif req["action"] == "archive" and not email.is_archived:
                return False
            elif req["action"] == "reply" and not email.is_read:
                return False
        
        return True

# Test the environment
if __name__ == "__main__":
    print("="*60)
    print("TESTING OPENENV-COMPLIANT EMAIL TRIAGE ENVIRONMENT")
    print("="*60)
    
    env = EmailTriageEnv()
    
    for task_id in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"TASK {task_id}")
        print(f"{'='*60}")
        
        obs = env.reset(task_id)
        print(f"Description: {obs.task_description}")
        print(f"Initial emails: {len(obs.visible_emails)}")
        print(f"Max actions: {obs.max_actions}")
        
        # Test some actions
        if task_id == 1:
            print("\nTesting actions...")
            obs, reward, done, info = env.step(Action("mark_spam", 1))
            print(f"  Marked spam: reward={reward}")
            obs, reward, done, info = env.step(Action("reply", 2, "Thank you!"))
            print(f"  Replied: reward={reward}")
        
        grade = env.grade()
        print(f"\nFinal Grade: {grade:.2f}/1.0")
        print(f"Total Reward: {obs.current_score:.2f}")
        
        # Show state
        state = env.state()
        print(f"Actions taken: {state['actions_taken']}/{state['max_actions']}")
    
    print(f"\n{'='*60}")
    print("✅ Environment is OpenEnv-compliant and ready!")
    print(f"{'='*60}")
