import os
import json
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)

model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

questions = [
    "What should I check before leaving for an Erasmus exchange?",
    "Which documents should I prepare for Erasmus registration?",
    "How can I check whether my courses will transfer as credits?",
    "What should I do if my host university has not sent an acceptance letter?",
    "How should I plan health insurance for studying abroad in Europe?",
    "What questions should I ask about accommodation before travelling?",
    "How can I make an exchange budget that includes hidden costs?",
    "What should I do if an official university webpage gives unclear instructions?",
    "Which deadlines should I put in an Erasmus preparation checklist?",
    "When should I contact my home university coordinator during an exchange?",
]

results = []

for i, question in enumerate(questions, start=1):
    print(f"Running question {i}/{len(questions)}...")
    started_at = time.perf_counter()

    try:
        response = client.models.generate_content(
            model=model,
            contents=question,
        )

        answer = response.text

    except Exception as error:
        answer = f"ERROR: {error}"

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    results.append({
        "question": question,
        "answer": answer,
        "latency_ms": latency_ms,
    })

    print(answer)
    print(f"Latency: {latency_ms} ms")
    print("-" * 40)

with open("experiment_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, indent=2, ensure_ascii=False)

print("Finished! Results saved to experiment_results.json")
