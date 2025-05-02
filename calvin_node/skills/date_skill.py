# calvin_node/skills/date_skill.py
import time

def can_handle(text: str) -> bool:
    kw = text.lower()
    return "date" in kw and ("what" in kw or "tell" in kw)

def run(text: str):
    today = time.localtime()
    return time.strftime("Today's date is %B %d, %Y", today)
