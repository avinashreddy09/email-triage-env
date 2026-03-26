from typing import Dict, List
from environment.models import Email

class TaskGrader:
    def __init__(self, task_id: int, required_actions: List[Dict], emails: List[Dict]):
        self.task_id = task_id
        self.required_actions = required_actions
        
    def grade(self, final_state: List[Email]) -> float:
        if not self.required_actions:
            return 1.0
            
        completed = 0
        for requirement in self.required_actions:
            action_type = requirement["action"]
            email_id = requirement["email_id"]
            
            email = next((e for e in final_state if e.id == email_id), None)
            if not email:
                continue
                
            if action_type == "mark_spam" and email.is_spam:
                completed += 1
            elif action_type == "archive" and email.is_archived:
                completed += 1
            elif action_type == "reply" and email.is_read:
                completed += 1
            elif action_type == "prioritize":
                if "priority" in requirement and email.priority == requirement["priority"]:
                    completed += 1
                    
        return completed / len(self.required_actions)
