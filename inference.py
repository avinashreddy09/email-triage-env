import os
import requests
import json
from openai import OpenAI

# Required environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")

# Check required token
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

SPACE_URL = os.getenv("SPACE_URL", "https://avinashreddy09-email-triage-agent.hf.space")

def run_inference():
    """Run inference on all 3 tasks with proper output format"""
    
    for task_id in [1, 2, 3]:
        task_name = {1: "easy", 2: "medium", 3: "hard"}[task_id]
        
        # START line
        print(f"[START] task={task_name} env=email-triage-agent model={MODEL_NAME}")
        
        # Reset environment
        resp = requests.post(f"{SPACE_URL}/reset?task_id={task_id}")
        if resp.status_code != 200:
            print(f"[END] success=false steps=0 rewards=0.00")
            continue
        
        # Get observation
        data = resp.json()
        observation = data.get("observation", data)
        
        rewards = []
        step = 1
        max_steps = observation.get("max_actions", 20)
        done = False
        
        while not done and step <= max_steps:
            # Build prompt for LLM
            prompt = f"""
You are an AI email assistant. Current task: {observation.get('task_description', '')}

Visible emails: {json.dumps(observation.get('visible_emails', [])[:3])}

Available actions: mark_spam, reply, archive, delete, mark_read, prioritize

Choose an action. Return JSON: {{"action_type": "mark_spam", "email_id": 1}}
"""
            
            try:
                # Call LLM
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=100
                )
                
                content = response.choices[0].message.content.strip()
                # Clean up response
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                action = json.loads(content)
                
                # Take step
                step_resp = requests.post(
                    f"{SPACE_URL}/step",
                    json={"action": action},
                    headers={"Content-Type": "application/json"}
                )
                
                if step_resp.status_code == 200:
                    step_data = step_resp.json()
                    reward = step_data.get("reward", 0.0)
                    done = step_data.get("done", False)
                    error = "null"
                    
                    rewards.append(reward)
                    
                    # STEP line
                    print(f"[STEP] step={step} action={action.get('action_type')} reward={reward:.2f} done={str(done).lower()} error={error}")
                else:
                    print(f"[STEP] step={step} action=error reward=-0.50 done=false error=step_failed")
                    rewards.append(-0.5)
                    
            except Exception as e:
                print(f"[STEP] step={step} action=error reward=-1.00 done=false error={str(e)}")
                rewards.append(-1.0)
            
            # Get fresh observation for next iteration
            state_resp = requests.get(f"{SPACE_URL}/state")
            if state_resp.status_code == 200:
                observation = state_resp.json()
            
            step += 1
        
        # Get final grade
        grade_resp = requests.get(f"{SPACE_URL}/grader")
        grade = grade_resp.json().get("grade", 0.0) if grade_resp.status_code == 200 else 0.0
        
        # END line
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])
        print(f"[END] success=true steps={step-1} rewards={rewards_str}")
        print(f"Grade: {grade:.2f}")  # Additional info

if __name__ == "__main__":
    run_inference()
