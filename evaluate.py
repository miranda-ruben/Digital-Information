import json
from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)

model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Find the project folder
PROJECT_DIR = Path(__file__).parent

# Find the expected answers file
ANSWERS_FILE = PROJECT_DIR / "expected_answers.json"

# Load the expected answers
with open(ANSWERS_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

questions = data["questions"]

print(f"Successfully loaded {len(questions)} test questions.")

for question in questions:
    print(f"Question {question['id']}: {question['question']}")
    print(f"Expected key points: {len(question['expected_key_points'])}")
    print()


def evaluate_answer(question, answer, expected_key_points):

  def evaluate_answer(question, answer, expected_key_points):
    evaluation_prompt = f"""
    You are evaluating the quality of an AI-generated answer
    about Erasmus student mobility at the University of Luxembourg.

    Original question:
    {question}

    Generated answer:
    {answer}

    Expected key points:
    {json.dumps(expected_key_points, ensure_ascii=False)}

    Evaluate each expected key point individually.

    A point is covered if the answer communicates its meaning,
    even if it uses different wording.

    Do not give credit for information that is not actually present.
    Do not assume that missing information is covered.

    Return your evaluation as JSON.
    """
