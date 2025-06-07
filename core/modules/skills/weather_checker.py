"""Weather checking skill using wttr.in service."""

import re
import requests

_pattern = re.compile(r"weather(?: in)? (?P<loc>[\w\s]+)?", re.IGNORECASE)


def can_handle(prompt: str) -> bool:
    return 'weather' in prompt.lower()


def handle(prompt: str) -> str:
    match = _pattern.search(prompt)
    location = match.group('loc').strip() if match and match.group('loc') else ''
    query = location if location else ''
    try:
        url = f'https://wttr.in/{query}?format=3'
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text.strip()
    except Exception:
        return "Unable to fetch weather right now."
