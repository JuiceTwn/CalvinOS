import asyncio
from shared.utils import send_to_core, receive_from_core
from .nlp import preprocess
# placeholder STT
async def stt():
    return input('You: ')

async def node_loop():
    while True:
        raw = await stt()
        processed = preprocess(raw)
        await send_to_core(raw, processed)
        resp = await receive_from_core()
        # placeholder TTS
        print(f"Calvin: {resp}")

if __name__ == '__main__':
    asyncio.run(node_loop())