import asyncio
from shared.utils import send_to_node, receive_from_node
from pathlib import Path

# dynamic skill loader
SKILLS_DIR = Path(__file__).parent / 'skills'
loaded_skills = {}

async def load_skills():
    for file in SKILLS_DIR.glob('*.py'):
        name = file.stem
        module = __import__(f'calvinos.core.skills.{name}', fromlist=[name])
        loaded_skills[name] = module

async def handle_request(raw_text, processed):
    # try local skills first
    for name, skill in loaded_skills.items():
        if skill.can_handle(processed):
            return await skill.run(processed)
    # fallback: use LLM
    from shared.utils import llm_generate
    return await llm_generate(raw_text, processed)

async def main_loop():
    await load_skills()
    while True:
        raw, processed = await receive_from_node()
        response = await handle_request(raw, processed)
        await send_to_node(response)

if __name__ == '__main__':
    asyncio.run(main_loop())