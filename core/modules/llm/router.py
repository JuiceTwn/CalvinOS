from modules.llm.thinker import Thinker
from modules.memory.memory import Memory
from modules.skills import handle_prompt

memory = Memory()

def route_input(prompt: str) -> str:
    # Check dynamic skills first
    skill_response = handle_prompt(prompt)
    if skill_response:
        memory.log("skill_used", f"{prompt} -> {skill_response}")
        return skill_response

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
