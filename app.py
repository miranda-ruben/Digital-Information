import math
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
    docs = []
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
            print(f"WARNING: {path.name} has no url/last_checked header and is NOT loaded.")
            continue

        check_dates[url] = to_dmy(checked)
        docs.append({
            "url": url,
            "checked": to_dmy(checked),
            "title": meta.get("title", path.stem),
            "text": text,
        })

    return docs, check_dates


SOURCES, SOURCE_CHECK_DATES = load_sources()
APPROVED_SOURCES = list(SOURCE_CHECK_DATES)

# ---- Choose the sources that fit the question (keeps the prompt small) ----
STOPWORDS = set(
    "a an the of to in on at for and or is are was were be been do does did can could "
    "should would will i my me we you your it its this that these those what which who "
    "whom when where why how with from by as if about into out up down over under than "
    "then so no not any some all get give tell please need want have has had there here "
    "much many more most also just".split()
)


# Different words that mean the same thing on the university pages.
ALIASES = {
    "apply": "application", "applying": "application", "applied": "application",
    "nomination": "allocation", "nominated": "allocation", "nominate": "allocation",
    "selection": "allocation", "selected": "allocation",
    "dispensation": "exemption", "dispense": "exemption",
    "abroad": "exchange", "mobility": "exchange",
}


def stem(word):
    word = ALIASES.get(word, word)
    for end in ("ing", "ed", "es", "s"):
        if word.endswith(end) and len(word) - len(end) >= 4:
            word = word[: -len(end)]
            break
    return word[:6]  # exempted / exemption -> exempt, application / applications -> applic


def words(text):
    found = re.findall(r"[a-z0-9+]+", text.lower())
    return [stem(w) for w in found if w not in STOPWORDS and len(w) > 1]


for doc in SOURCES:
    doc["counts"] = {}
    for w in words(doc["text"]):
        doc["counts"][w] = doc["counts"].get(w, 0) + 1
    doc["title_words"] = set(words(doc["title"] + " " + doc["url"]))

DOC_FREQ = {}
for doc in SOURCES:
    for w in doc["counts"]:
        DOC_FREQ[w] = DOC_FREQ.get(w, 0) + 1


def select_sources(question, limit=6):
    """Return the `limit` documents that best match the question (best first)."""
    terms = set(words(question))
    scored = []
    for doc in SOURCES:
        score = 0.0
        for w in terms:
            tf = doc["counts"].get(w, 0)
            if tf:
                idf = math.log((len(SOURCES) + 1) / (1 + DOC_FREQ[w])) + 1
                score += (1 + math.log(tf)) * idf
            if w in doc["title_words"]:
                score += 3
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:limit]]


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

    selected = select_sources(question)
    if not selected:
        # Nothing in the official sources even mentions the question's words.
        return jsonify({"answer": VALID_REFUSAL})

    source_text = "\n\n".join(
        f"=== SOURCE ===\nURL: {d['url']}\nLast checked: {d['checked']}\n\n{d['text']}"
        for d in selected
    )
    selected_dates = {d["url"]: d["checked"] for d in selected}

    try:
        response = client.models.generate_content(
            model=model,
            contents=f"""
            Answer the user's question using only the official source text below.
            Do not add any facts from your general knowledge.
            If the source contains part of the answer, give that part and say
            clearly what the source does not cover. Do not invent the rest.
            Only if the source contains nothing useful for the question, reply:
            "{VALID_REFUSAL}"
            Sources marked as no longer offered or outdated must be reported as such.
            Answer in plain text.
            Do not use Markdown formatting such as ** or *.
            Cite every answer with one or more exact approved official source URLs.

            Official source:
            {source_text}

            User question:
            {question}

            Everytime you cite a source, include the last checked date of that source in the format "Last checked: DD.MM.YYYY".
            If no date is available, use "Last checked: unknown".
            Last checked dates of the official sources:
            {selected_dates}
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