from modules.llm.thinker import Thinker
from modules.memory.memory import Memory

memory = Memory()

def route_input(prompt: str) -> str:
    model = Thinker()

    try:
        response = model.generate(prompt)
        if "*error*" in response.lower() or not response.strip():
            memory.log("skill_suggestion", prompt, tags=["fallback", "unrecognized"])
        return response

    except Exception as e:
        print(f"Router error: {e}")
        memory.log("skill_suggestion", prompt, tags=["exception"])
        return "I was unable to process that. It’s been logged for improvement."
