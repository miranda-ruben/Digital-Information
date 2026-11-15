import json
from pathlib import Path

# Find the project folder
PROJECT_DIR = Path(__file__).parent

# Find the expected answers file
ANSWERS_FILE = PROJECT_DIR / "expected_answers.json"

# Load the expected answers
with open(ANSWERS_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

questions = data["questions"]

print(f"Successfully loaded {len(questions)} test questions.")