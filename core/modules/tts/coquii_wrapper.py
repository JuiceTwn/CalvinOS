from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import tempfile
import os
import logging

class TTSWrapper:
    def __init__(self, model_name: str = "tts_models/en/vctk/vits"):
        # Lighter VITS model, British-ish (trained on VCTK dataset)
        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

    def speak(self, text: str):
        """Generate speech and play it. Uses temp WAV file."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
                output_file = tf.name

            self.tts.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=None,
                language="en"
            )

            data, fs = sf.read(output_file, dtype='float32')
            sd.play(data, fs)
            sd.wait()
            os.remove(output_file)

        except Exception as e:
            logging.error(f"🛑 TTS failed: {e}")
            print(f"💥 Calvin lost his voice: {e}")
