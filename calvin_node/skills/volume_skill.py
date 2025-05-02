# calvin_node/skills/volume_skill.py
import subprocess
import re

def can_handle(text: str) -> bool:
    kw = text.lower()
    return any(word in kw for word in ("volume", "louder", "quieter", "mute"))

def run(text: str):
    # This example uses `amixer` on Linux; swap out for your OS.
    if "mute" in text.lower():
        subprocess.run(["amixer", "set", "Master", "mute"])
        return "Volume muted."
    if "louder" in text.lower() or "up" in text.lower():
        subprocess.run(["amixer", "set", "Master", "5%+"])
        return "Turning it up a notch."
    if "quieter" in text.lower() or "down" in text.lower():
        subprocess.run(["amixer", "set", "Master", "5%-"])
        return "Dialing it down."
    return "Volume command not recognized."
