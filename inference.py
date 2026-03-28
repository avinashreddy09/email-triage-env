"""
Inference Script for Email Triage Environment
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    
- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables
"""

import os
import json
import requests
from openai import OpenAI
from typing import Dict, Any, List

# Environment variables (required for the hackathon)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
SPACE_URL = os.getenv("SPACE_URL", "https://avinashreddy09-email-triage-env.hf.space")

MAX_STEPS = 20
TEMPERATURE = 0.2
MAX_TOKENS = 200

class EmailTriageAgent:
    """Agent that uses LLM to manage emails"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )
    
    def get_action(self, observation: Dict, task_id: int) -> Dict:
        """Get next action from LLM"""
        
        # Format visible emails
        emails = observation.get("visible_emails", [])
        if not emails:
            return {"action_type": "noop", "email_id": 1}
        
        # Build prompt
        prompt = f"""
You are an AI email assistant. Current task ID: {task_id}

Task Description: {observation.get('task_description', '')}

Visible emails:
{self._format_emails(emails)}

Actions taken so far: {observation.get('actions_taken', 0)}/{observation.get('max_actions', 20)}
Current score: {observation.get('current_score', 0):.2f}

Available actions:
- mark_spam: Mark email as spam (takes email_id)
- reply: Reply to email (takes email_id, reply_content)
- archive: Archive email (takes email_id)
- delete: Delete email (takes email_id)
- mark_read: Mark as read (takes email_id)
- prioritize: Change priority (takes email_id, new_priority: low/normal/high/urgent)

Choose the next action. Return ONLY a JSON object with:
{{"action_type": "reply", "email_id": 2, "reply_content": "Thank you for your email"}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an email assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up response
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error: {e}, using fallback action")
            return {"action_type": "archive", "email_id": emails[0]["id"]}
    
    def _format_emails(self, emails: List[Dict]) -> str:
        """Format emails for prompt"""
        formatted = []
        for email in emails[:5]:  # Limit to 5
            formatted.append(
                f"ID: {email['id']} | From: {email['sender']}\n"
                f"Subject: {email['subject']}\n"
                f"Body: {email['body'][:100]}...\n"
            )
        return "\n".join(formatted)

def run_task(task_id: int, agent: EmailTriageAgent) -> float:
    """Run a single task and return the grade"""
    print(f"\n{'='*50}")
    print(f"Running Task {task_id}")
    print(f"{'='*50}")
    
    # Reset environment
    response = requests.post(f"{SPACE_URL}/reset?task_id={task_id}")
    if response.status_code != 200:
        print(f"Failed to reset: {response.status_code}")
        return 0.0
    
    obs_data = response.json()
    observation = obs_data.get("observation", {})
    
    print(f"Task: {observation.get('task_description', 'Unknown')}")
    print(f"Initial emails: {len(observation.get('visible_emails', []))}")
    
    done = False
    step_count = 0
    max_actions = observation.get("max_actions", 20)
    
    while not done and step_count < max_actions:
        print(f"\nStep {step_count + 1}/{max_actions}")
        print(f"Current score: {observation.get('current_score', 0):.2f}")
        
        # Get action from LLM
        action = agent.get_action(observation, task_id)
        print(f"Action: {action.get('action_type')} on email {action.get('email_id')}")
        
        # Take step
        response = requests.post(
            f"{SPACE_URL}/step",
            json={"action": action},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"Step failed: {response.status_code}")
            break
        
        result = response.json()
        observation = result.get("observation", {})
        reward = result.get("reward", 0)
        done = result.get("done", False)
        
        print(f"Reward: {reward:.2f} - {result.get('info', {}).get('reason', '')}")
        
        step_count += 1
    
    # Get final grade
    response = requests.get(f"{SPACE_URL}/grader")
    if response.status_code == 200:
        grade = response.json().get("grade", 0.0)
        print(f"\nFinal Grade: {grade:.2f}/1.0")
        return grade
    
    return 0.0

def main():
    """Main inference function"""
    print("="*60)
    print("EMAIL TRIAGE INFERENCE SCRIPT")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Space URL: {SPACE_URL}")
    
    # Check required environment variables
    if not API_KEY:
        print("\n⚠️  ERROR: HF_TOKEN or API_KEY not set!")
        print("Please set environment variable: HF_TOKEN=your_token")
        return
    
    # Initialize agent
    agent = EmailTriageAgent()
    
    # Run all 3 tasks
    grades = []
    for task_id in [1, 2, 3]:
        grade = run_task(task_id, agent)
        grades.append(grade)
    
    # Print results
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for i, grade in enumerate(grades, 1):
        print(f"Task {i}: {grade:.2f}/1.0")
    
    avg_grade = sum(grades) / len(grades) if grades else 0
    print(f"\nAverage Grade: {avg_grade:.2f}/1.0")
    print("="*60)

if __name__ == "__main__":
    main()
