from TTS.api import TTS
import sounddevice as sd

class TTSWrapper:
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        # Coqui TTS model; pick yours from https://huggingface.co/models?filter=tts
        self.tts = TTS(model_name)

    def speak(self, text: str, output_file: str = "calvin_out.wav"):
        """Generate audio and play it, returns path to WAV."""
        wav = self.tts.tts(text=text)
        self.tts.save_wav(wav, output_file)
        # auto-play
        data, fs = self.tts.load_wav(output_file)
        sd.play(data, fs)
        sd.wait()
        return output_file
