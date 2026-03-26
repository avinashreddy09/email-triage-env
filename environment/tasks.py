TASKS = {
    1: {
        "name": "Easy: Simple Email Filtering",
        "description": "You have 3 emails. Archive the spam email and reply to the customer inquiry.",
        "emails": [
            {"id": 1, "sender": "spam@unknown.com", "subject": "WINNER!", "body": "You won!", "priority": "normal", "is_spam": True},
            {"id": 2, "sender": "customer@example.com", "subject": "Product Question", "body": "Tell me about pricing", "priority": "normal"},
            {"id": 3, "sender": "newsletter@company.com", "subject": "Newsletter", "body": "Weekly update", "priority": "low"}
        ],
        "required_actions": [
            {"action": "mark_spam", "email_id": 1},
            {"action": "reply", "email_id": 2}
        ],
        "max_actions": 10
    },
    2: {
        "name": "Medium: Priority Management",
        "description": "Handle 8 emails with different priorities",
        "emails": [
            {"id": 1, "sender": "ceo@company.com", "subject": "URGENT Meeting", "body": "Meeting in 1 hour", "priority": "urgent"},
            {"id": 2, "sender": "client@bigcorp.com", "subject": "Contract", "body": "Review contract", "priority": "high"},
            {"id": 3, "sender": "spammer@fake.com", "subject": "Buy watches", "body": "Cheap watches", "priority": "normal", "is_spam": True},
            {"id": 4, "sender": "colleague@company.com", "subject": "Lunch", "body": "Want lunch?", "priority": "low"},
            {"id": 5, "sender": "newsletter@tech.com", "subject": "Tech News", "body": "Tech updates", "priority": "low"},
            {"id": 6, "sender": "newsletter@marketing.com", "subject": "Marketing Tips", "body": "Marketing strategies", "priority": "low"},
            {"id": 7, "sender": "support@company.com", "subject": "Complaint", "body": "Product defective", "priority": "high"},
            {"id": 8, "sender": "meeting@calendar.com", "subject": "Schedule Meeting", "body": "Propose times", "priority": "normal"}
        ],
        "required_actions": [
            {"action": "reply", "email_id": 1},
            {"action": "prioritize", "email_id": 2, "priority": "high"},
            {"action": "mark_spam", "email_id": 3},
            {"action": "archive", "email_id": 4},
            {"action": "archive", "email_id": 5},
            {"action": "archive", "email_id": 6},
            {"action": "reply", "email_id": 8}
        ],
        "max_actions": 20
    },
    3: {
        "name": "Hard: Complex Workflow",
        "description": "Complex email thread requiring escalation",
        "emails": [
            {"id": 1, "sender": "angry_customer@gmail.com", "subject": "COMPLAINT", "body": "Product broken", "priority": "urgent"},
            {"id": 2, "sender": "escalation@manager.com", "subject": "URGENT Escalation", "body": "Client threatening", "priority": "urgent"},
            {"id": 3, "sender": "partner@vendor.com", "subject": "Partnership", "body": "Discuss partnership", "priority": "high"},
            {"id": 4, "sender": "phishing@fakebank.com", "subject": "Account compromised", "body": "Click here", "priority": "normal", "is_spam": True},
            {"id": 5, "sender": "colleague@team.com", "subject": "Project Update", "body": "Need status", "priority": "high"},
            {"id": 6, "sender": "spam@advertising.com", "subject": "Make money", "body": "Work from home", "priority": "normal", "is_spam": True},
            {"id": 7, "sender": "customer@support.com", "subject": "Follow-up", "body": "Following up", "priority": "normal"},
            {"id": 8, "sender": "newsletter@industry.com", "subject": "Weekly Digest", "body": "Industry news", "priority": "low"}
        ],
        "required_actions": [
            {"action": "reply", "email_id": 1},
            {"action": "prioritize", "email_id": 1, "priority": "urgent"},
            {"action": "reply", "email_id": 2},
            {"action": "reply", "email_id": 3},
            {"action": "mark_spam", "email_id": 4},
            {"action": "reply", "email_id": 5},
            {"action": "mark_spam", "email_id": 6},
            {"action": "reply", "email_id": 7},
            {"action": "archive", "email_id": 8}
        ],
        "max_actions": 25
    }
}
