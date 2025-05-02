# calvin_node/skills/math_skill.py
import re

# simple pattern: “what is 3 plus 4” or “calculate 12 * 5”
PATTERN = re.compile(r"(-?\d+)\s*(plus|\+|minus|\-|times|\*|divided by|/)\s*(-?\d+)")

def can_handle(text: str) -> bool:
    return bool(PATTERN.search(text.lower()))

def run(text: str):
    match = PATTERN.search(text.lower())
    if not match:
        return "I couldn't parse your math."
    a, op, b = match.groups()
    a, b = int(a), int(b)
    if op in ("plus", "+"):
        res = a + b
    elif op in ("minus", "-"):
        res = a - b
    elif op in ("times", "*"):
        res = a * b
    elif op in ("divided by", "/"):
        res = a / b if b != 0 else "∞"
    else:
        return "Unknown operator."
    return f"{a} {op} {b} equals {res}"
