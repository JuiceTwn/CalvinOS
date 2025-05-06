import logging
from modules.stt.vosk_wrapper import STT
from modules.nlp.nlp_wrapper import NLP
from modules.llm.thinker import Thinker
from modules.tts.coquii_wrapper import TTSWrapper
from modules.memory.memory import Memory

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

def run_cli():
    stt = STT()
    nlp = NLP()
    thinker = Thinker()
    tts = TTSWrapper()
    memory = Memory()

    logging.info("Calvin CLI is active. Press Ctrl+C to exit.")
    while True:
        try:
            text = stt.listen()
            logging.info(f"🗣️ Heard: {text}")

            intent = nlp.interpret(text)
            logging.debug(f"💡 Intent: {intent}")

            response = thinker.generate(text)
            logging.info(f"🤖 Responding with: {response}")

            memory.log("interaction", f"You said: {text} → Calvin replied: {response}")
            tts.speak(response)

        except KeyboardInterrupt:
            logging.info("CLI mode terminated by user.")
            break
        except Exception as e:
            logging.error(f"🔥 Runtime error in CLI: {str(e)}", exc_info=True)
            print(f"[ERROR] Something went wrong: {e}")
