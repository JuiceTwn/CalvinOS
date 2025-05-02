#!/usr/bin/env python3
# calvin_node/main.py

import os
import sys
import time
import uuid
import logging
import threading
import importlib.util
import json
from pathlib import Path

import httpx
import openai
from vosk import Model, KaldiRecognizer
import pyaudio
from TTS.api import TTS

# ─── CONFIG ────────────────────────────────────────────────────────────────────
CORE_URL        = os.getenv("CALVIN_CORE_URL", "http://localhost:8000")
API_TOKEN       = os.getenv("CALVIN_CORE_TOKEN", "changeme")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
NODE_ID         = os.getenv("NODE_ID", str(uuid.getnode()) or str(uuid.uuid4()))
NODE_TYPE       = os.getenv("NODE_TYPE", "pc_test_node")
POLL_DELAY      = float(os.getenv("NODE_POLL_DELAY", 5.0))
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
TTS_MODEL       = os.getenv("TTS_MODEL", "tts_models/en/vctk/vits")

# ─── LOGGING ───────────────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info(f"Node {NODE_ID} ({NODE_TYPE}) starting up.")

# ─── SKILL LOADER ───────────────────────────────────────────────────────────────
skills = {}

def load_skills():
    skills_dir = Path(__file__).parent / "skills"
    logging.info(f"🔍 Loading skills from {skills_dir}")
    if not skills_dir.exists():
        logging.warning("No skills/ folder found.")
        return
    for file in skills_dir.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(file.stem, str(file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            if hasattr(module, "can_handle") and hasattr(module, "run"):
                skills[file.stem] = module
                logging.info(f"✅ Loaded skill: {file.stem}")
            else:
                logging.warning(f"⚠️  Skill {file.stem} missing interface.")
        except Exception as e:
            logging.error(f"❌ Failed to load skill {file.stem}: {e}")

# ─── STT / TTS SETUP ─────────────────────────────────────────────────────────────
if not os.path.isdir(VOSK_MODEL_PATH):
    logging.error(f"Vosk model not found at {VOSK_MODEL_PATH}.")
    sys.exit(1)
vosk_model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)
tts = TTS(TTS_MODEL, progress_bar=False, gpu=False)

# ─── HTTP CLIENT ────────────────────────────────────────────────────────────────
class NodeClient:
    def __init__(self):
        self.client = httpx.Client(timeout=10.0)
        self.headers = {"X-API-Token": API_TOKEN}
        openai.api_key = OPENAI_API_KEY

    def register(self):
        url = f"{CORE_URL}/node_sync"
        payload = {"node_id": NODE_ID, "info": {"type": NODE_TYPE, "id": NODE_ID}}
        logging.info(f"Registering node → {url}")
        resp = self.client.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        logging.info(f"✅ Registered: {resp.json()}")

    def send_heartbeat(self):
        url = f"{CORE_URL}/status"
        try:
            resp = self.client.get(url, headers=self.headers)
            resp.raise_for_status()
        except Exception as e:
            logging.warning(f"Heartbeat failed: {e}")

    def send_core_command(self, cmd: str):
        url = f"{CORE_URL}/command"
        logging.info(f"→ Core command: {cmd}")
        resp = self.client.post(url, json={"cmd": cmd}, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("result", "")

    def ask_openai(self, prompt: str) -> str:
        logging.info("🤖 Querying OpenAI GPT-3.5-turbo fallback")
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()

# ─── PREPROCESSING PIPELINE ─────────────────────────────────────────────────────
FILLERS = {"um","uh","like","basically","you know","just","kinda","sort of","maybe"}
ADDRESS_KEYWORDS = {"assistant","calvin","computer"}
VERB_STARTS = {"tell","set","run","what","open","play","stop"}

def preprocess_text(text: str):
    raw = text.strip()
    lower = raw.lower()
    tokens = lower.split()
    fillers = [t for t in tokens if t in FILLERS]
    cleaned_tokens = [t for t in tokens if t not in FILLERS]
    cleaned = " ".join(cleaned_tokens)
    tone = {
        "uncertainty": fillers.count("maybe")+fillers.count("kinda"),
        "questions": raw.count("?"),
        "exclaims": raw.count("!")
    }
    return cleaned, fillers, tone

def detect_address(cleaned: str):
    score = 0
    if any(cleaned.startswith(v) for v in VERB_STARTS): score += 1
    if "please" in cleaned: score += 1
    if any(k in cleaned for k in ADDRESS_KEYWORDS): score += 2
    return score >= 1

# Light keyword‐scoring intent classifier
def classify_intent(cleaned: str):
    # build keyword map once
    keyword_map = {
        name: getattr(mod, "KEYWORDS", [])
        for name, mod in skills.items()
    }
    scores = {}
    words = set(cleaned.split())
    for name, kws in keyword_map.items():
        match = words.intersection(kws)
        if match:
            scores[name] = len(match)/len(kws)
    if not scores:
        return None
    best, score = max(scores.items(), key=lambda x: x[1])
    return best if score >= 0.2 else None

def speak(text: str):
    logging.info(f"🎙️ Speaking: {text}")
    wav = tts.tts(text)
    tts.save_wav(wav, "response.wav")
    os.system("aplay response.wav")

# ─── MAIN PROCESSOR ─────────────────────────────────────────────────────────────
def process_text(text: str, client: NodeClient):
    cleaned, fillers, tone = preprocess_text(text)
    logging.debug(f"Cleaned: {cleaned} | Tone: {tone} | Fillers: {fillers}")

    if not detect_address(cleaned):
        logging.debug("Not addressed to Calvin.")
        return

    # Direct GPT prefix
    if cleaned.startswith(("ai:","gpt:","openai:")):
        prompt = cleaned.split(":",1)[1].strip()
        resp = client.ask_openai(prompt)
        speak(resp)
        return

    # Rule‐based
    for name, mod in skills.items():
        if mod.can_handle(cleaned):
            resp = mod.run(cleaned)
            if isinstance(resp, dict) and resp.get("core_cmd"):
                client.send_core_command(resp["core_cmd"])
            speak(resp.get("speak", resp) if isinstance(resp, dict) else resp)
            return

    # Keyword‐score fallback
    intent = classify_intent(cleaned)
    if intent:
        logging.info(f"⭐ Routed via keyword score to {intent}")
        resp = skills[intent].run(cleaned)
        speak(resp)
        return

    # Final fallback
    resp = client.ask_openai(cleaned)
    speak(resp)

# ─── WORKER THREADS & MAIN LOOP ─────────────────────────────────────────────────
def start_heartbeat(client: NodeClient):
    while True:
        client.send_heartbeat()
        time.sleep(POLL_DELAY)

def listen_and_transcribe():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                     input=True, frames_per_buffer=8000)
    stream.start_stream()
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result()).get("text","")
            if res:
                logging.info(f"🎤 Heard: {res}")
                return res

def main():
    setup_logging()
    load_skills()
    client = NodeClient()
    client.register()
    threading.Thread(target=start_heartbeat, args=(client,), daemon=True).start()

    try:
        while True:
            text = listen_and_transcribe()
            process_text(text, client)
    except KeyboardInterrupt:
        logging.info("🛑 Node shutdown.")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()
