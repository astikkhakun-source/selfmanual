import re
import json
import os

TECH_SPECS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Tech_specs.md")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "questions_v1_2.json")

def parse_questions():
    with open(TECH_SPECS_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Match pattern: Q001 — `cognitive_openness` · `D` · `TRAIT` \n\n Text
    pattern = re.compile(
        r"Q(\d{3})\s+—\s+`([^`]+)`\s+·\s+`([^`]+)`\s+·\s+`([^`]+)`\s*\n+([^\n]+)"
    )

    questions = {}
    for match in pattern.finditer(text):
        q_num = match.group(1)
        q_id = f"Q{q_num}"
        scale_id = match.group(2).replace("\\", "")
        direction = match.group(3)
        q_type = match.group(4)
        q_text = match.group(5).strip()

        questions[q_id] = {
            "id": q_id,
            "scale_id": scale_id,
            "direction": direction,
            "type": q_type,
            "text_ru": q_text
        }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Successfully parsed {len(questions)} questions into {OUTPUT_PATH}")

if __name__ == "__main__":
    parse_questions()
