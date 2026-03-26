from typing import Dict, Any, Tuple, List
from datetime import datetime
from environment.models import Email, Action, Observation
from environment.tasks import TASKS
from environment.graders import TaskGrader

class EmailEnv:
    def __init__(self):
        self.emails = []
        self.current_task_id = 1
        self.task_description = ""
        self.actions_taken = 0
        self.max_actions = 10
        self.current_reward = 0.0
        self.done = False
        self.grader = None
        self.required_actions = []
        
    def reset(self, task_id: int = 1) -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Task {task_id} not found")
            
        task = TASKS[task_id]
        
        self.emails = []
        for email_data in task["emails"]:
            email = Email(
                id=email_data["id"],
                sender=email_data["sender"],
                subject=email_data["subject"],
                body=email_data["body"],
                priority=email_data.get("priority", "normal"),
                is_spam=email_data.get("is_spam", False),
                timestamp=datetime.now()
            )
            self.emails.append(email)
            
        self.current_task_id = task_id
        self.task_description = task["description"]
        self.actions_taken = 0
        self.max_actions = task["max_actions"]
        self.current_reward = 0.0
        self.done = False
        self.required_actions = task["required_actions"]
        
        self.grader = TaskGrader(task_id, task["required_actions"], task["emails"])
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        if self.done:
            raise RuntimeError("Episode already done")
            
        email = next((e for e in self.emails if e.id == action.email_id), None)
        if not email:
            return self._get_observation(), -0.5, False, {"error": "Email not found"}
        
        reward_value = 0.0
        
        if action.action_type == "reply":
            if action.reply_content:
                email.is_read = True
                reward_value = 0.5
        elif action.action_type == "archive":
            email.is_archived = True
            reward_value = 0.2
        elif action.action_type == "delete":
            email.is_archived = True
            reward_value = 0.3
        elif action.action_type == "mark_spam":
            email.is_spam = True
            email.is_archived = True
            reward_value = 0.8
        elif action.action_type == "mark_read":
            email.is_read = True
            reward_value = 0.1
            
        self.actions_taken += 1
        self.current_reward += reward_value
        
        if self.actions_taken >= self.max_actions:
            self.done = True
            
        if self._check_all_required_completed():
            self.done = True
            reward_value += 2.0
        
        return self._get_observation(), reward_value, self.done, {}
    
    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.current_task_id,
            "actions_taken": self.actions_taken,
            "max_actions": self.max_actions,
            "current_reward": self.current_reward,
            "done": self.done
        }
    
    def grade(self) -> float:
        if not self.done:
            return 0.0
        return self.grader.grade(self.emails)
    
    def _get_observation(self) -> Observation:
        visible_emails = [e for e in self.emails if not e.is_archived]
        return Observation(
            visible_emails=visible_emails,
            current_task_description=self.task_description,
            actions_taken_so_far=self.actions_taken,
            max_actions=self.max_actions,
            current_score=self.current_reward,
            task_id=self.current_task_id
        )
    
    def _check_all_required_completed(self) -> bool:
        if not self.required_actions:
            return False
            
        for requirement in self.required_actions:
            action_type = requirement["action"]
            email_id = requirement["email_id"]
            
            email = next((e for e in self.emails if e.id == email_id), None)
            if not email:
                return False
                
            if action_type == "mark_spam" and not email.is_spam:
                return False
            elif action_type == "archive" and not email.is_archived:
                return False
            elif action_type == "reply" and not email.is_read:
                return False
                    
        return True
