# core/llm/local_mistral.py
import openai

openai.api_key = "ollama"  # Doesn't matter, Ollama doesn't check
openai.api_base = "http://localhost:11434/v1"

def ask_local_llm(prompt: str, history: list = []):
    messages = [
        {"role": "system", "content": "You are Calvin. Be confident, efficient, short. You are running locally."}
    ]
    messages += history
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="mistral",
        messages=messages,
        temperature=0.2,
        max_tokens=100
    )

    return response.choices[0].message.content.strip()
