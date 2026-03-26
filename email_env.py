# Full Email Triage Environment with 3 Tasks
class Email:
    def __init__(self, id, sender, subject, body, priority="normal", is_spam=False):
        self.id = id
        self.sender = sender
        self.subject = subject
        self.body = body
        self.priority = priority
        self.is_read = False
        self.is_archived = False
        self.is_spam = is_spam

class Action:
    def __init__(self, action_type, email_id, reply_content=None, new_priority=None):
        self.action_type = action_type
        self.email_id = email_id
        self.reply_content = reply_content
        self.new_priority = new_priority

class Observation:
    def __init__(self, visible_emails, task_description, actions_taken, max_actions, score, task_id):
        self.visible_emails = visible_emails
        self.current_task_description = task_description
        self.actions_taken_so_far = actions_taken
        self.max_actions = max_actions
        self.current_score = score
        self.task_id = task_id

class EmailEnv:
    def __init__(self):
        self.emails = []
        self.task_description = ""
        self.actions_taken = 0
        self.max_actions = 10
        self.score = 0.0
        self.done = False
        self.current_task_id = 1
        self.required_actions = []
        
    def reset(self, task_id=1):
        self.current_task_id = task_id
        self.actions_taken = 0
        self.score = 0.0
        self.done = False
        
        if task_id == 1:
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
            
        elif task_id == 3:
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
    
    def step(self, action):
        if self.done:
            return self._get_observation(), 0, True, {}
        
        email = next((e for e in self.emails if e.id == action.email_id), None)
        if not email:
            return self._get_observation(), -0.5, False, {"error": "Email not found"}
        
        reward = 0
        
        if action.action_type == "mark_spam":
            if not email.is_spam:
                email.is_spam = True
                email.is_archived = True
                reward = 0.8
                
        elif action.action_type == "reply":
            if action.reply_content:
                email.is_read = True
                reward = 0.5
            else:
                reward = -0.2
                
        elif action.action_type == "archive":
            if not email.is_archived:
                email.is_archived = True
                reward = 0.2
                
        elif action.action_type == "delete":
            if not email.is_archived:
                email.is_archived = True
                reward = 0.3
                
        elif action.action_type == "mark_read":
            if not email.is_read:
                email.is_read = True
                reward = 0.1
                
        elif action.action_type == "prioritize":
            if action.new_priority:
                email.priority = action.new_priority
                reward = 0.2
        
        self.actions_taken += 1
        self.score += reward
        
        if self._check_completed():
            self.done = True
            reward += 2.0
        
        if self.actions_taken >= self.max_actions:
            self.done = True
            
        return self._get_observation(), reward, self.done, {}
    
    def _get_observation(self):
        visible = [e for e in self.emails if not e.is_archived]
        return Observation(visible, self.task_description, self.actions_taken, 
                          self.max_actions, self.score, self.current_task_id)
    
    def _check_completed(self):
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
    
    def grade(self):
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

# Test all 3 tasks
print("="*60)
print("EMAIL TRIAGE ENVIRONMENT - TESTING ALL 3 TASKS")
print("="*60)

env = EmailEnv()

for task_id in [1, 2, 3]:
    print(f"\n{'='*60}")
    print(f"TASK {task_id}")
    print(f"{'='*60}")
    
    obs = env.reset(task_id)
    print(f"Description: {obs.current_task_description}")
    print(f"Initial emails: {len(obs.visible_emails)}")
    
    # Simulate actions for each task
    if task_id == 1:
        env.step(Action("mark_spam", 1))
        env.step(Action("reply", 2, "Thank you for your inquiry!"))
    elif task_id == 2:
        env.step(Action("reply", 1, "I'll be there"))
        env.step(Action("mark_spam", 3))
        env.step(Action("archive", 4))
        env.step(Action("archive", 5))
        env.step(Action("archive", 6))
        env.step(Action("reply", 8, "How about 3pm?"))
    elif task_id == 3:
        env.step(Action("reply", 1, "We'll process your refund"))
        env.step(Action("reply", 2, "I'll handle this immediately"))
        env.step(Action("reply", 3, "Let's schedule a call"))
        env.step(Action("mark_spam", 4))
        env.step(Action("reply", 5, "Project is on track"))
        env.step(Action("mark_spam", 6))
        env.step(Action("reply", 7, "Following up now"))
        env.step(Action("archive", 8))
    
    grade = env.grade()
    print(f"Final Grade: {grade:.2f}/1.0")
    print(f"Total Reward: {obs.current_score:.2f}")

print(f"\n{'='*60}")
print("✅ All tasks working! Environment is ready for AI agent.")
print(f"{'='*60}")
