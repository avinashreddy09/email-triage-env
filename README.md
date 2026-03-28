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

- **Task 1 (Easy)**: Archive spam and reply to customer inquiry (10 actions)
- **Task 2 (Medium)**: Handle urgent emails and manage priorities (20 actions)
- **Task 3 (Hard)**: Handle complaints, escalations, and multiple priorities (25 actions)

## License

MIT
