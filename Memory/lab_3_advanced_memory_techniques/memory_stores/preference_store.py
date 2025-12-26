"""Preference Memory Store - KV store for user preferences (tone, devices, communication style)."""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pathlib import Path


class PreferenceMemoryStore:
    """KV store for user preferences (tone, devices, communication style).
    
    NOTE: Preferences are written only via explicit calls (preference_store.put()).
    There is no automatic LLM-based preference detection. This is by design to
    ensure preferences are only set when explicitly requested by the user.
    """
    
    def __init__(self, file_path: str = "preferences.json"):
        self.file_path = Path(file_path)
        self._load()
    
    def _load(self):
        """Load preferences from disk."""
        if self.file_path.exists():
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}
    
    def _save(self):
        """Save preferences to disk."""
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get a preference value."""
        return self.data.get(namespace, {}).get(key)
    
    def get_all(self, namespace: str) -> Dict[str, Any]:
        """Get all preferences for a namespace."""
        return self.data.get(namespace, {})
    
    def put(self, namespace: str, key: str, value: Any):
        """Set a preference value."""
        if namespace not in self.data:
            self.data[namespace] = {}
        self.data[namespace][key] = {
            "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        self._save()
    
    def delete(self, namespace: str, key: str):
        """Delete a preference."""
        if namespace in self.data and key in self.data[namespace]:
            del self.data[namespace][key]
            self._save()

