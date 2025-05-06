from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from modules.llm.router import route_input
from modules.memory.memory import Memory

app = FastAPI()
memory = Memory()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class Prompt(BaseModel):
    prompt: str

@app.post("/chat")
def chat(prompt: Prompt):
    logging.info(f"📩 Incoming request: {prompt.prompt}")
    try:
        response = route_input(prompt.prompt)
        memory.log("api_interaction", f"{prompt.prompt} → {response}")
        logging.info(f"📤 Response: {response}")
        return {"response": response}
    except Exception as e:
        logging.error(f"🔥 Exception during /chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error. Check logs for details.")
