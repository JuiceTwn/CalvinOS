from modules.stt.vosk_wrapper import STT
from modules.nlp.nlp_wrapper import NLP
from modules.llm.thinker import Thinker
from modules.tts.coquii_wrapper import TTSWrapper
from modules.memory.memory import Memory

def run_cli():
    stt = STT()
    nlp = NLP()
    thinker = Thinker()
    tts = TTSWrapper()
    memory = Memory()

    print("Calvin CLI active.")
    while True:
        try:
            text = stt.listen()
            intent = nlp.interpret(text)
            response = thinker.generate(text)
            memory.log("interaction", f"You said: {text} → Calvin replied: {response}")
            tts.speak(response)
        except KeyboardInterrupt:
            break
