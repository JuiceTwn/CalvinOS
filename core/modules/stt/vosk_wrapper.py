import os, json, queue, logging, platform
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from vosk import SetLogLevel

SetLogLevel(-1)  # quiet down Vosk logs

class STT:
    def __init__(self, model_path: str = None):
        base_path = os.path.dirname(os.path.abspath(__file__))

        if model_path is None:
            # Absolute model path fallback
            model_path = os.path.join(base_path, "vosk-model-en-us-0.22")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"🛑 Vosk model not found at: {model_path}")

        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.q = queue.Queue()
        self.enabled = self._check_mic_support()

    def _check_mic_support(self) -> bool:
        """ Disable mic support if running in WSL or no input device available. """
        try:
            if "microsoft" in platform.uname().release.lower():
                logging.warning("WSL detected — disabling microphone input.")
                return False
            sd.query_devices(kind='input')  # will throw if none found
            return True
        except Exception as e:
            logging.warning(f"No input device found: {e}")
            return False

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Mic stream status: {status}")
        self.q.put(bytes(indata))

    def listen(self, duration: int = 5) -> str:
        """ Record from mic or fallback to keyboard if disabled. """
        if not self.enabled:
            return input("🔹 Type input (no mic): ")

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000,
                                   dtype='int16', channels=1,
                                   callback=self._callback):
                print("🎙️ Listening...")
                sd.sleep(duration * 1000)
        except Exception as e:
            logging.error(f"🎤 Mic error: {e}")
            return input("🔹 Mic failed, type input instead: ")

        result = ""
        while not self.q.empty():
            data = self.q.get()
            if self.rec.AcceptWaveform(data):
                res = json.loads(self.rec.Result())
                result += res.get("text", "") + " "
        final = json.loads(self.rec.FinalResult())
        result += final.get("text", "")
        return result.strip()
