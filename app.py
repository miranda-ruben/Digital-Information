import os
import re
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai.errors import ServerError, ClientError

# Website runs on http://127.0.0.1:5000
app = Flask(__name__)

SOURCE_DIR = Path(__file__).parent / "university_sources"

# The two older .txt files have no header, so their details are listed here.
LEGACY_SOURCES = {
    "erasmus-application.txt": {
        "url": "https://www.uni.lu/en/mobility/outgoing-student-mobility/erasmus/",
        "last_checked": "2026-11-12",
    },
    "study-abroad.txt": {
        "url": "https://www.uni.lu/fdef-en/study-abroad/",
        "last_checked": "2026-11-12",
    },
}


def read_header(text):
    """Read the 'key: value' lines between the two --- lines at the top of a .md file."""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
    return meta


def to_dmy(iso_date):
    """2026-11-12 -> 12.11.2026 (unchanged if it is not in that format)."""
    parts = iso_date.split("-")
    return f"{parts[2]}.{parts[1]}.{parts[0]}" if len(parts) == 3 else iso_date


def load_sources():
    documents = []
    check_dates = {}

    for path in sorted(SOURCE_DIR.glob("*.md")) + sorted(SOURCE_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".md":
            meta = read_header(text)
        else:
            meta = LEGACY_SOURCES.get(path.name, {})

        url = meta.get("url")
        checked = meta.get("last_checked")
        if not url or not checked:
            continue  # not an official source (for example GAPS.md)

        check_dates[url] = to_dmy(checked)
        documents.append(
            f"=== SOURCE ===\nURL: {url}\nLast checked: {to_dmy(checked)}\n\n{text}"
        )

    return "\n\n".join(documents), check_dates


SOURCE_TEXT, SOURCE_CHECK_DATES = load_sources()
APPROVED_SOURCES = list(SOURCE_CHECK_DATES)

VALID_REFUSAL = (
    "I couldn't find this in the official information available to me. "
    "Please consult the University's Erasmus+ guidance or contact the "
    "relevant mobility office."
)

URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")



@app.get("/")
def home():
    return send_from_directory(".", "index.html")


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def check_source(answer):
    if not isinstance(answer, str) or not answer.strip():
        return False

    if " ".join(answer.split()) == VALID_REFUSAL:
        return True

    citations = [
        match.rstrip(".,;:!?)]}")
        for match in URL_PATTERN.findall(answer)
    ]

    return bool(citations) and all(
        citation in APPROVED_SOURCES for citation in citations
    )


def get_source_dates(answer):
    citations = [
        match.rstrip(".,;:!?)]}")
        for match in URL_PATTERN.findall(answer)
    ]

    sources = []

    for citation in dict.fromkeys(citations):
        if citation in SOURCE_CHECK_DATES:
            sources.append({
                "url": citation,
                "last_checked": SOURCE_CHECK_DATES[citation]
            })

    return sources


@app.post("/ask")
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a University of Luxembourg related question."
        }), 400

    try:
        response = client.models.generate_content(
            model=model,
            contents=f"""
            Answer the user's question using only the official source text below.
            Do not add any facts from your general knowledge.
            If the source does not answer the question, reply:
            "{VALID_REFUSAL}"
            Answer in plain text.
            Do not use Markdown formatting such as ** or *.
            Cite every answer with one or more exact approved official source URLs.

            Official source:
            {SOURCE_TEXT}

            User question:
            {question}

            Everytime you cite a source, include the last checked date of that source in the format "Last checked: DD.MM.YYYY".
            If no date is available, use "Last checked: unknown".
            Last checked dates of the official sources:
            {SOURCE_CHECK_DATES}
            """,
        )

    
    except ClientError as e:
        if e.code == 429:
            return jsonify({
                "error": "Gemini's request limit has been reached. Please try again later."
            }), 429

        app.logger.exception("Gemini API request failed.")
        return jsonify({
            "error": "There was a problem processing your request."
        }), 502

    except ServerError:
        app.logger.exception("Gemini is temporarily unavailable.")
        return jsonify({
            "error": "Gemini is temporarily unavailable. Please try again later."
        }), 503


    if not check_source(response.text or ""):
        return jsonify({
            "answer": "I couldn't verify this answer using the approved university sources."
        })

   
    return jsonify({
        "answer": response.text,
        "sources": get_source_dates(response.text or "")
    })

if __name__ == "__main__":
    app.run(debug=True)