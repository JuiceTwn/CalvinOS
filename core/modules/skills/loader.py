import os
import importlib.util

SKILL_DIR = os.path.dirname(__file__)

_loaded_skills = []

def _load_skills():
    global _loaded_skills
    _loaded_skills = []
    for fname in os.listdir(SKILL_DIR):
        if fname.endswith('.py') and fname not in ('__init__.py', 'loader.py'):
            path = os.path.join(SKILL_DIR, fname)
            spec = importlib.util.spec_from_file_location(fname[:-3], path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                _loaded_skills.append(module)

_load_skills()

def reload_skills():
    _load_skills()


def handle_prompt(prompt: str):
    for mod in _loaded_skills:
        try:
            can = getattr(mod, 'can_handle', None)
            handle = getattr(mod, 'handle', None)
            if callable(can) and can(prompt) and callable(handle):
                return handle(prompt)
        except Exception:
            continue
    return None
