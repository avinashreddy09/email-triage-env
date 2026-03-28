import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
SPACE_URL = os.getenv("SPACE_URL", "https://avinashreddy09-email-triage-agent.hf.space")

def main():
    print("Running inference...")
    for task_id in [1, 2, 3]:
        try:
            resp = requests.post(f"{SPACE_URL}/reset?task_id={task_id}")
            print(f"Task {task_id}: {resp.status_code}")
            grade_resp = requests.get(f"{SPACE_URL}/grader")
            grade = grade_resp.json().get("grade", 0)
            print(f"  Grade: {grade}")
        except Exception as e:
            print(f"Error on task {task_id}: {e}")

if __name__ == "__main__":
    main()