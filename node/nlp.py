INTENT_KEYWORDS = {
    'greet': ['hello', 'hi', 'hey'],
    'time': ['time', 'date'],
}

def preprocess(text: str):
    lower = text.lower()
    tokens = lower.split()
    intents = [intent for intent, keys in INTENT_KEYWORDS.items() if any(k in tokens for k in keys)]
    return {
        'tokens': tokens,
        'intents': intents,
    }