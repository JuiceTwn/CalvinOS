# node/skill_loader.py
import os
import importlib.util

def load_skills(skills_dir: str = os.path.join(os.path.dirname(__file__), 'skills')):
    skills = []
    for fname in os.listdir(skills_dir):
        if not fname.endswith('.py') or fname.startswith('_'):
            continue
        path = os.path.join(skills_dir, fname)
        spec = importlib.util.spec_from_file_location(fname[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'can_handle') and hasattr(mod, 'run'):
            skills.append(mod)
    return skills

# Example usage in node/main.py:
# from node.skill_loader import load_skills
# skills = load_skills()
# for skill in skills:
#     if skill.can_handle(processed):
#         response = await skill.run(processed)