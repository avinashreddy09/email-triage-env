import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
SPACE_URL = os.getenv("SPACE_URL", "https://avinashreddy09-email-triage-agent.hf.space")

def main():
    print("OpenEnv Inference Script")
    print("="*50)
    
    results = []
    for task_id in [1, 2, 3]:
        print(f"\nTask {task_id}:")
        
        # Reset
        resp = requests.post(f"{SPACE_URL}/reset?task_id={task_id}")
        print(f"  Reset: {resp.status_code}")
        
        # Take some actions
        actions = [
            {"action": {"action_type": "mark_spam", "email_id": 1}},
            {"action": {"action_type": "reply", "email_id": 2, "reply_content": "Thank you!"}}
        ]
        
        for action in actions:
            step_resp = requests.post(f"{SPACE_URL}/step", json=action)
            print(f"  Step: {step_resp.status_code}")
        
        # Get grade
        grade_resp = requests.get(f"{SPACE_URL}/grader")
        grade = grade_resp.json().get("grade", 0)
        results.append(grade)
        print(f"  Grade: {grade}")
    
    print(f"\nAverage Grade: {sum(results)/len(results):.2f}")

if __name__ == "__main__":
    main()
