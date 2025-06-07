"""Simple Spotify music player skill placeholder."""

import re

_trigger = re.compile(r"play\s+(?P<song>.+)", re.IGNORECASE)


def can_handle(prompt: str) -> bool:
    return bool(_trigger.search(prompt))


def handle(prompt: str) -> str:
    match = _trigger.search(prompt)
    if match:
        song = match.group('song').strip()
        song = re.sub(r'on spotify$', '', song, flags=re.IGNORECASE).strip()
        if song:
            return f"Playing {song} on Spotify."
    return "Opening Spotify and playing your music."
