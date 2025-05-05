def count_tokens(text: str) -> int:
    # Very basic token estimate (doesn't use tiktoken)
    return len(text.split())

def truncate_to_limit(text: str, max_tokens: int) -> str:
    tokens = text.split()
    return " ".join(tokens[:max_tokens])
