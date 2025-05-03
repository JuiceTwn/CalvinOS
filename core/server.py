# core/server.py
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from shared.logger import get_logger
from core.tts import synthesize
from core.stt import transcribe

logger = get_logger(__name__)
app = FastAPI()
clients = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    logger.info("🧩 Node connected")
    try:
        while True:
            data = await ws.receive_bytes()
            # STT: audio bytes -> text
            raw_text = transcribe(data)
            logger.debug(f"[STT] Got text: {raw_text}")

            # Core logic placeholder: echo back
            response_text = f"You said: {raw_text}"

            # TTS: text -> audio bytes
            audio_bytes = synthesize(response_text)
            logger.debug(f"[TTS] Sending audio of length {len(audio_bytes)}")

            # send back as binary
            await ws.send_bytes(audio_bytes)
    except WebSocketDisconnect:
        clients.remove(ws)
        logger.info("🧩 Node disconnected")