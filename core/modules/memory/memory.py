import os, json
from datetime import datetime
from typing import List, Optional, Dict

MEMORY_DIR = "data"
MEMORY_FILE = os.path.join(MEMORY_DIR, "calvin_memory.json")
BACKUP_FILE = os.path.join(MEMORY_DIR, "calvin_memory_backup.json")

class Memory:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.memory = self._load_memory()

    def _load_memory(self) -> List[Dict]:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print("⚠️ Memory file corrupted. Starting fresh.")
                    return []
        return []

    def _save_memory(self):
        # Optional: write backup first
        with open(BACKUP_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)
        # Then save actual memory file
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)

    def log(self, type_: str, content: str, tags: Optional[List[str]] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": type_,
            "content": content,
            "tags": tags or []
        }
        self.memory.append(entry)
        self._save_memory()

    def get_by_type(self, type_: str) -> List[Dict]:
        return [entry for entry in self.memory if entry["type"] == type_]

    def search(self, keyword: str, type_filter: Optional[str] = None) -> List[Dict]:
        results = []
        for entry in self.memory:
            if keyword.lower() in entry["content"].lower():
                if not type_filter or entry["type"] == type_filter:
                    results.append(entry)
        return results

    def clear_type(self, type_: str):
        self.memory = [entry for entry in self.memory if entry["type"] != type_]
        self._save_memory()

    def get_latest(self, count: int = 5) -> List[Dict]:
        return self.memory[-count:]

    def dump_all(self) -> List[Dict]:
        return self.memory.copy()
