import os, json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class STT:
    def __init__(self, model_path: str = "models/vosk-model-small-en-us-0.15"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(bytes(indata))

    def listen(self, duration: int = 5) -> str:
        """ Record `duration` seconds from mic and return the transcribed text. """
        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype='int16', channels=1,
                               callback=self._callback):
            sd.sleep(duration * 1000)

        result = ""
        while not self.q.empty():
            data = self.q.get()
            if self.rec.AcceptWaveform(data):
                res = json.loads(self.rec.Result())
                result += res.get("text", "") + " "
        final = json.loads(self.rec.FinalResult())
        result += final.get("text", "")
        return result.strip()
