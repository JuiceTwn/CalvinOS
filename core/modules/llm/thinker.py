import os, json, requests
from requests.exceptions import Timeout as RequestsTimeout, RequestException
from modules.llm.prompt import get_personality_prompt  # ✅ import here

API_HOST = os.getenv("OLLAMA_API_HOST", "http://localhost:11434")
API_BASE = f"{API_HOST}/v1"
MODEL = os.getenv("OLLAMA_MODEL", "mistral")
MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "150"))
TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "8"))
CHUNK_SIZE = 25

class Thinker:
    def __init__(self):
        self.session = requests.Session()
        self.personality = get_personality_prompt()

    def generate(self, prompt: str) -> str:
        url = f"{API_BASE}/chat/completions"
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": self.personality},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "stream": True
        }

        try:
            r = self.session.post(url, json=payload, timeout=TIMEOUT, stream=True)
            r.raise_for_status()
        except (RequestsTimeout, RequestException):
            print("Calvin: *connection issue*")
            return "*error*"

        print("Calvin:", end=" ", flush=True)
        buffer, out = [], []

        for line in r.iter_lines(decode_unicode=True):
            if not line or line.startswith("data: [DONE]"):
                continue
            if line.startswith("data: "):
                line = line[6:]
            try:
                obj = json.loads(line)
                token = obj["choices"][0]["delta"].get("content")
                if token:
                    buffer.append(token)
                    out.append(token)
                    if len(buffer) >= CHUNK_SIZE:
                        print("".join(buffer), end="", flush=True)
                        buffer.clear()
            except (json.JSONDecodeError, KeyError):
                continue

        if buffer:
            print("".join(buffer), end="", flush=True)
        print()
        return "".join(out).strip()
