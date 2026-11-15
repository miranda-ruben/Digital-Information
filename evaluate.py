import json
from pathlib import Path
import os
from google.genai import errors
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

# Find the generated results file
RESULTS_FILE = PROJECT_DIR / "experiment_results.json"

# Load the expected answers
with open(ANSWERS_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

questions = data["questions"]

# Load the generated results
with open(RESULTS_FILE, "r", encoding="utf-8") as file:
    generated_results = json.load(file)

print(f"Successfully loaded {len(generated_results)} generated answers.")
print(f"Successfully loaded {len(questions)} test questions.")

# Match each question with its generated answer
for question, result in zip(questions, generated_results):
    print(f"Question: {question['question']}")
    print(f"Generated answer: {result['answer']}")
    print("-" * 40)



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

    Return ONLY valid JSON in this exact format:

    {{
        "results": [
            {{
                "key_point": "The expected key point",
                "covered": true,
                "explanation": "Why this point was considered covered or missing"
            }}
        ]
    }}

    Include exactly one result for every expected key point.
    Use true or false for covered.
    Do not include Markdown formatting or code fences.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=evaluation_prompt
        )

        return response.text

    except errors.APIError as error:
        print(f"Gemini API error: {error}")
        return None



