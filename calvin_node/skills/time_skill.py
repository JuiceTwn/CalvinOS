# calvin_node/skills/time_skill.py
import time

def can_handle(text: str) -> bool:
    kw = text.lower()
    return "time" in kw and ("what" in kw or "tell" in kw)

def run(text: str):
    now = time.localtime()
    return time.strftime("Current time is %I:%M %p", now)
