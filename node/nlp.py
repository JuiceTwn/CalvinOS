# nlp.py (advanced light NLP engine)
import re
import unicodedata
from typing import List, Dict
from collections import Counter

# Intent keyword map (expandable)
INTENT_KEYWORDS = {
    'greet': ['hello', 'hi', 'hey', 'yo'],
    'time': ['time', 'clock', 'hour', 'what time'],
    'date': ['date', 'day', 'today', 'calendar'],
    'weather': ['weather', 'forecast', 'temperature', 'rain', 'snow'],
    'reminder': ['remind', 'reminder', 'note', 'remember'],
    'joke': ['joke', 'funny', 'laugh'],
    'exit': ['bye', 'exit', 'quit', 'leave'],
}

# Common filler/noise words
FILLERS = {
    'um', 'uh', 'like', 'you know', 'er', 'ah', 'so', 'just', 'actually', 'literally'
}

# Simple synonyms/expansions
SYNONYMS = {
    'whats': 'what is',
    'wanna': 'want to',
    'gonna': 'going to',
    'tellme': 'tell me',
    'gotta': 'got to',
    'gotcha': 'got you',
    'btw': 'by the way',
    'idk': "i don't know",
}

def normalize(text: str) -> str:
    """Clean and normalize input text."""
    text = text.lower()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r"[^a-z0-9'\s]", "", text)
    for slang, standard in SYNONYMS.items():
        text = text.replace(slang, standard)
    return text

def tokenize(text: str) -> List[str]:
    tokens = text.split()
    return [t for t in tokens if t not in FILLERS]

def detect_intents(tokens: List[str]) -> List[str]:
    matched = []
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in tokens for k in keywords):
            matched.append(intent)
    return matched

def detect_command(tokens: List[str]) -> str:
    # crude priority if multiple intents exist
    command = detect_intents(tokens)
    return command[0] if command else 'unknown'

def get_keyword_counts(tokens: List[str]) -> Dict[str, int]:
    return dict(Counter(tokens))

def preprocess(text: str) -> Dict:
    clean = normalize(text)
    tokens = tokenize(clean)
    intents = detect_intents(tokens)
    keyword_freq = get_keyword_counts(tokens)

    return {
        'original': text,
        'normalized': clean,
        'tokens': tokens,
        'intents': intents,
        'primary_intent': detect_command(tokens),
        'keyword_frequency': keyword_freq,
    }
