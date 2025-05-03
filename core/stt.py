# core/stt.py
from shared.logger import get_logger
from shared.config import Config

logger = get_logger(__name__)

# Example using faster-whisper (placeholder)
def transcribe(audio_bytes: bytes) -> str:
    """
    Transcribe speech audio bytes to text.
    Replace this placeholder with your chosen STT engine integration.
    """
    logger.info(f"[STT] Received audio bytes: {len(audio_bytes)} bytes")
    # TODO: integrate faster_whisper or whisper-cpp here
    # e.g., transcript = whisper_model.transcribe(audio_bytes)
    # return transcript

    # Fallback: return dummy text for testing
    return "hello calvin"