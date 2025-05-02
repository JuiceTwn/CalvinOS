# calvin_node/skills/joke_skill.py
import random

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the function return early? It had commitment issues.",
    "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'"
]

def can_handle(text: str) -> bool:
    kw = text.lower()
    return "joke" in kw or "funny" in kw

def run(text: str):
    return random.choice(JOKES)
