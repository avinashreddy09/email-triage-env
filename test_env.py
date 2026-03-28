from environment.email_env import EmailEnv
from environment.models import Action

print("Testing Email Triage Environment...")
print("="*50)

env = EmailEnv()
obs = env.reset(task_id=1)
print(f"Task: {obs.current_task_description}")
print(f"Emails: {len(obs.visible_emails)}")

action = Action(action_type="mark_spam", email_id=1)
obs, reward, done, info = env.step(action)
print(f"Marked spam - Reward: {reward}")

action = Action(action_type="reply", email_id=2, reply_content="Thanks")
obs, reward, done, info = env.step(action)
print(f"Replied - Reward: {reward}")

grade = env.grade()
print(f"Final Grade: {grade}")

print("="*50)
print("Environment is working!")
