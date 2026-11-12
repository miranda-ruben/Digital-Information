import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai.errors import ServerError

# Website runs on http://127.0.0.1:5000
app = Flask(__name__)

SOURCE_DIR = Path(__file__).parent / "university_sources"
SOURCE_FILES = [
    SOURCE_DIR / "erasmus-application.txt",
    SOURCE_DIR / "study-abroad.txt",
]
SOURCE_TEXT = "\n".join(file.read_text(encoding="utf-8") for file in SOURCE_FILES)


@app.get("/")
def home():
    return send_from_directory(".", "index.html")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

@app.post("/ask")
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a University of Luxembourg related question."}), 400

    try:
        response = client.models.generate_content(
            model=model,
            contents=f"""
            Answer the user's question using only the official source text below.
            Do not add any facts from your general knowledge.
            If the source does not answer the question, reply:
            "I couldn't find this in the official information available to me. Please consult the University's secreatary office."

            Official source:
            {SOURCE_TEXT}

            User question:
            {question}
            """,
        )
    except ServerError:
        app.logger.exception("Gemini is temporarily unavailable.")
        return jsonify({
            "error": "Gemini is temporarily unavailable. Please try again later."
        }), 503

    return jsonify({"answer": response.text})

if __name__ == "__main__":
    app.run(debug=True)
