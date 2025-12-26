"""Ticket management tools."""
import json
from datetime import datetime, timezone
from pathlib import Path

# Load ticket DB
ticket_file = Path(__file__).parent.parent.parent / "data" / "tickets.json"

def _load_ticket_db():
    """Load ticket database from file."""
    try:
        with open(ticket_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def _save_ticket_db(db):
    """Save ticket database to file."""
    try:
        # Ensure parent directory exists
        ticket_file.parent.mkdir(parents=True, exist_ok=True)
        # Write to file
        with open(ticket_file, "w") as f:
            json.dump(db, f, indent=2)
        # Verify write by reading back
        with open(ticket_file, "r") as f:
            verify_db = json.load(f)
            if len(verify_db) != len(db):
                raise Exception(f"Write verification failed: expected {len(db)} tickets, got {len(verify_db)}")
    except Exception as e:
        raise Exception(f"Failed to save ticket database: {str(e)}")

# Initialize ticket DB
ticket_db = _load_ticket_db()


def lookup_ticket_tool(ticket_id: str):
    """Lookup ticket by ID."""
    global ticket_db
    # Reload from file to ensure we have latest data
    ticket_db = _load_ticket_db()
    ticket = ticket_db.get(ticket_id)
    if ticket is None:
        return {"error": f"Ticket {ticket_id} not found."}
    return {"ticket": ticket, "ticket_id": ticket_id}


def create_ticket_tool(customer_name: str, issue: str, device: str = "-", priority: str = "Medium"):
    """Create a new ticket."""
    global ticket_db
    # Reload to ensure we have latest data before creating
    ticket_db = _load_ticket_db()
    
    # Generate new ticket ID
    existing_ids = [int(k) for k in ticket_db.keys() if k.isdigit()]
    new_id = str(max(existing_ids, default=0) + 1)
    
    # Create ticket
    ticket_db[new_id] = {
        "status": "New",
        "issue": issue,
        "description": issue,
        "device": device,
        "priority": priority,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "customer_name": customer_name,
        "notes": [{"timestamp": datetime.now(timezone.utc).isoformat(), "author": "customer", "text": issue}]
    }
    
    # Save to file with verification
    try:
        _save_ticket_db(ticket_db)
        # Verify the ticket was saved by reloading
        verify_db = _load_ticket_db()
        if new_id not in verify_db:
            raise Exception(f"Ticket {new_id} was not found after save. File path: {ticket_file.resolve()}")
        # Update global ticket_db to match saved state
        ticket_db = verify_db
    except Exception as e:
        error_msg = f"Failed to save ticket: {str(e)}"
        return {"error": error_msg, "ticket_id": new_id, "ticket": ticket_db.get(new_id), "file_path": str(ticket_file.resolve())}
    
    result = {"ticket_id": new_id, "status": "created", "message": f"Ticket {new_id} created successfully", "ticket": ticket_db[new_id], "file_path": str(ticket_file.resolve())}
    return result


def update_ticket_tool(ticket_id: str, note: str = None, device: str = None, status: str = None):
    """Add a note or update device/status info to an existing ticket."""
    global ticket_db
    
    # Reload to ensure we have latest data before updating
    ticket_db = _load_ticket_db()
    
    if ticket_id not in ticket_db:
        return {"error": f"Ticket {ticket_id} not found."}
    
    ticket = ticket_db[ticket_id]
    
    # Update fields
    if note:
        if "notes" not in ticket:
            ticket["notes"] = []
        ticket["notes"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author": "customer",
            "text": note
        })
    
    if device and device != "-":
        ticket["device"] = device
    
    if status:
        ticket["status"] = status
    
    ticket["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Save to file
    _save_ticket_db(ticket_db)
    
    return {"ticket_id": ticket_id, "status": "updated", "ticket": ticket}


TOOLS = [
    {"name": "lookup_ticket", "func": lambda args: lookup_ticket_tool(args["ticket_id"])},
    {"name": "create_ticket", "func": lambda args: create_ticket_tool(**args)},
    {"name": "update_ticket", "func": lambda args: update_ticket_tool(**args)}
]
