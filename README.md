@'
---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Email Triage OpenEnv Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-brightgreen)](https://github.com/openenv)

A real-world email management simulation for AI agents, built for the OpenEnv Hackathon.

## Environment Description

This environment simulates an email inbox where AI agents must perform triage tasks:
- Replying to emails
- Archiving newsletters
- Marking spam
- Managing priorities
- Handling complaints and escalations

## API Endpoints

- `POST /reset?task_id=1` - Reset environment
- `POST /step` - Take an action
- `GET /state` - Get current state
- `GET /baseline` - Run baseline inference
- `GET /grader` - Get final grade
- `GET /tasks` - List available tasks

## Tasks

| ID | Name | Difficulty | Max Actions |
|----|------|------------|-------------|
| 1 | Simple Email Filtering | Easy | 10 |
| 2 | Priority Management | Medium | 20 |
| 3 | Complex Workflow | Hard | 25 |

## Quick Test

```bash
# Reset environment
curl -X POST https://avinashreddy09-email-triage-env.hf.space/reset?task_id=1

# Mark spam
curl -X POST https://avinashreddy09-email-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"action_type": "mark_spam", "email_id": 1}}'
