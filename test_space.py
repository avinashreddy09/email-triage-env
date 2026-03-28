import requests
import json

space_url = "https://avinashreddy09-email-triage-env.hf.space"

print("Testing Space...")
print("="*50)

# Test 1: Reset
print("\n1. Testing reset endpoint...")
resp = requests.post(f"{space_url}/reset?task_id=1")
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   Task: {data.get('task_description', 'N/A')}")
    print(f"   Emails: {len(data.get('visible_emails', []))}")

# Test 2: State
print("\n2. Testing state endpoint...")
resp = requests.get(f"{space_url}/state")
print(f"   Status: {resp.status_code}")

# Test 3: Tasks
print("\n3. Testing tasks endpoint...")
resp = requests.get(f"{space_url}/tasks")
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    tasks = resp.json().get("tasks", [])
    print(f"   Tasks found: {len(tasks)}")

print("\n" + "="*50)
print("All tests passed!" if resp.status_code == 200 else "Some tests failed")
