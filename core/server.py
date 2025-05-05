from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.modules.llm.router import route_input
from core.modules.memory.memory import Memory

app = FastAPI()
memory = Memory()

class Prompt(BaseModel):
    prompt: str

@app.post("/chat")
def chat(prompt: Prompt):
    try:
        response = route_input(prompt.prompt)
        memory.log("api_interaction", f"{prompt.prompt} → {response}")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
