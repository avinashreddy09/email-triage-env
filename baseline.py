"""Baseline inference script using OpenAI API"""

import os
import json
from typing import Dict, List
from environment import EmailTriageEnv, Action, Observation

class BaselineAgent:
    """Simple baseline agent using GPT"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️  No OpenAI API key found. Using random actions.")
            self.use_openai = False
        else:
            self.use_openai = True
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("⚠️  OpenAI library not installed. Using random actions.")
                self.use_openai = False
        
        self.env = EmailTriageEnv()
    
    def get_action_from_llm(self, observation: Observation) -> Action:
        """Get next action from GPT"""
        if not self.use_openai:
            return self._get_random_action(observation)
        
        # Create prompt
        prompt = f"""
You are an AI email assistant. Current task: {observation.task_description}

Visible emails:
{self._format_emails(observation.visible_emails)}

Actions taken: {observation.actions_taken}/{observation.max_actions}
Current score: {observation.current_score:.2f}

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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up response
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            action_dict = json.loads(content)
            return Action(**action_dict)
            
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return self._get_random_action(observation)
    
    def _get_random_action(self, observation: Observation) -> Action:
        """Fallback: return a simple action"""
        if observation.visible_emails:
            email_id = observation.visible_emails[0]["id"]
            return Action("archive", email_id)
        return Action("mark_read", 1)
    
    def _format_emails(self, emails: List[Dict]) -> str:
        """Format emails for prompt"""
        if not emails:
            return "No visible emails."
        
        formatted = []
        for email in emails[:5]:  # Limit to 5 emails
            formatted.append(
                f"ID: {email['id']} | From: {email['sender']}\n"
                f"Subject: {email['subject']}\n"
                f"Body: {email['body'][:100]}...\n"
            )
        return "\n".join(formatted)
    
    def run_task(self, task_id: int) -> Dict:
        """Run a single task"""
        print(f"\n{'='*50}")
        print(f"Running Task {task_id}")
        print(f"{'='*50}")
        
        observation = self.env.reset(task_id)
        print(f"Task: {observation.task_description}")
        print(f"Initial emails: {len(observation.visible_emails)}")
        
        done = False
        step_count = 0
        
        while not done and step_count < observation.max_actions:
            print(f"\nStep {step_count + 1}/{observation.max_actions}")
            print(f"Current score: {observation.current_score:.2f}")
            
            # Get action
            action = self.get_action_from_llm(observation)
            print(f"Action: {action.action_type} on email {action.email_id}")
            
            # Take step
            observation, reward, done, info = self.env.step(action)
            print(f"Reward: {reward:.2f} - {info.get('reason', '')}")
            
            step_count += 1
        
        # Get final grade
        final_grade = self.env.grade()
        print(f"\n{'='*50}")
        print(f"Task {task_id} Complete!")
        print(f"Final Grade: {final_grade:.2f}/1.0")
        print(f"Total Reward: {observation.current_score:.2f}")
        print(f"Steps Taken: {step_count}")
        
        return {
            "task_id": task_id,
            "grade": final_grade,
            "reward": observation.current_score,
            "steps": step_count
        }
    
    def run_all_tasks(self) -> Dict:
        """Run all three tasks"""
        results = []
        for task_id in [1, 2, 3]:
            result = self.run_task(task_id)
            results.append(result)
        
        avg_grade = sum(r["grade"] for r in results) / 3
        return {"results": results, "average_grade": avg_grade}

def main():
    """Main entry point"""
    print("="*60)
    print("EMAIL TRIAGE BASELINE AGENT")
    print("="*60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not found in environment variables")
        print("You can set it with: $env:OPENAI_API_KEY='your-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key-here")
        print("\nRunning with random actions...\n")
    
    # Run baseline
    agent = BaselineAgent()
    results = agent.run_all_tasks()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for result in results["results"]:
        print(f"Task {result['task_id']}: Grade = {result['grade']:.2f}/1.0 (Steps: {result['steps']})")
    print(f"\nAverage Grade: {results['average_grade']:.2f}/1.0")
    print("="*60)

if __name__ == "__main__":
    main()
