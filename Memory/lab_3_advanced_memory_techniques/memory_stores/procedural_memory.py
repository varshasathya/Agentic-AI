"""Procedural Memory - Structured prompts and rules for agent behavior."""

import json
from datetime import datetime
from typing import Dict, Any, Optional


class ProceduralMemory:
    """Structured prompts and rules for agent behavior."""
    
    ESCALATION_RULES = {
        "critical": {
            "threshold": "priority == 'Critical' or status == 'Escalated'",
            "action": "escalate_to_level2",
            "message": "Issue escalated to Level 2 support due to critical priority."
        },
        "high_priority_3_days": {
            "threshold": "priority == 'High' and age_days >= 3",
            "action": "escalate_to_level2",
            "message": "High priority ticket open for 3+ days, escalating."
        }
    }
    
    DIAGNOSTIC_ORDER = [
        "1. Check ticket status and priority",
        "2. Retrieve relevant memories (semantic + episodic)",
        "3. If device info missing, ask for device model",
        "4. If issue unclear, ask for specific symptoms",
        "5. Suggest troubleshooting steps based on issue type",
        "6. If unresolved after 2 attempts, escalate"
    ]
    
    TOOL_USAGE_RULES = {
        "create_ticket": {
            "required_fields": ["customer_name", "issue"],
            "optional_fields": ["device", "priority"],
            "default_priority": "Medium"
        },
        "update_ticket": {
            "requires_ticket_id": True,
            "can_update": ["note", "device", "status"],
            "note_required": False
        },
        "lookup_ticket": {
            "requires_ticket_id": True,
            "use_when": "user asks for status, details, or history"
        }
    }
    
    PROCEDURES = {
        "standard_support": {
            "name": "Standard Support Flow",
            "steps": DIAGNOSTIC_ORDER,
            "allowed_tools": ["create_ticket", "update_ticket", "lookup_ticket"],
            "escalation_rules": ["critical", "high_priority_3_days"]
        },
        "quick_resolution": {
            "name": "Quick Resolution Flow",
            "steps": [
                "1. Check if issue matches known quick fixes",
                "2. Apply quick fix if available",
                "3. If not, escalate to standard flow"
            ],
            "allowed_tools": ["lookup_ticket"],
            "escalation_rules": []
        },
        "escalated_support": {
            "name": "Escalated Support Flow",
            "steps": [
                "1. Review escalation reason",
                "2. Gather all context (memories + ticket history)",
                "3. Apply Level 2 diagnostic procedures",
                "4. Document resolution path"
            ],
            "allowed_tools": ["lookup_ticket", "update_ticket"],
            "escalation_rules": []
        }
    }
    
    @classmethod
    def get_escalation_decision(cls, ticket: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if ticket should be escalated based on rules."""
        priority = ticket.get("priority", "Medium")
        status = ticket.get("status", "New")
        created_at = ticket.get("created_at", "")
        
        # Check critical escalation
        if priority == "Critical" or status == "Escalated":
            return cls.ESCALATION_RULES["critical"]
        
        # Check high priority age
        if priority == "High" and created_at:
            try:
                created = datetime.fromisoformat(created_at)
                age_days = (datetime.now() - created).days
                if age_days >= 3:
                    return cls.ESCALATION_RULES["high_priority_3_days"]
            except:
                pass
        
        return None
    
    @classmethod
    def get_procedural_prompt(cls) -> str:
        """Get structured procedural instructions."""
        return f"""
        You are a CRM support agent following structured procedures:

        DIAGNOSTIC ORDER:
        {chr(10).join(cls.DIAGNOSTIC_ORDER)}

        TOOL USAGE RULES:
        {json.dumps(cls.TOOL_USAGE_RULES, indent=2)}

        ESCALATION RULES:
        - Critical priority → escalate immediately
        - High priority + 3+ days old → escalate
        - Unresolved after 2 troubleshooting attempts → escalate

        Always follow this order and rules. Do not invent new procedures.
        """

