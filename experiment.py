
import json
from os import error
import time
from app import client, model, select_sources, VALID_REFUSAL
from prompt import build_prompt


with open("expected_answers.json", "r", encoding="utf-8") as file:
    test_cases = json.load(file)["questions"]

results = []

for i, case in enumerate(test_cases, start=1):
    question = case["question"]
    expected_key_points = case["expected_key_points"]
    print(f"Running question {i}/{len(test_cases)}...")
    started_at = time.perf_counter()

    try:
        selected = select_sources(question)

        if not selected:
            answer = VALID_REFUSAL
        else:
            source_text = "\n\n".join(
                f"=== SOURCE ===\nURL: {doc['url']}\nLast checked: {doc['checked']}\n\n{doc['text']}"
                for doc in selected
            )

            selected_dates = {
                doc["url"]: doc["checked"]
                for doc in selected
            }


            response = client.models.generate_content(
                model=model,
                contents=build_prompt(
                    source_text,
                    question,
                    selected_dates,
                    VALID_REFUSAL
                ),
            )

            answer = response.text

    except Exception as error:
        answer = f"ERROR: {error}"

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    results.append({
        "question": question,
        "expected_key_points": expected_key_points,
        "answer": answer,
        "latency_ms": latency_ms,
    })

    print(answer)
    print(f"Latency: {latency_ms} ms")
    print("-" * 40)

with open("experiment_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, indent=2, ensure_ascii=False)

print("Finished! Results saved to experiment_results.json")
