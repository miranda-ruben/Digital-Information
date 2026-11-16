# UniGuide AI: Milestone 2 & 3
https://github.com/miranda-ruben/Digital-Information (Public)
**Chosen approach:** Gemini API, `gemini-3.5-flash-lite`
## Milestone 3

## How to Run UniGuideAI

**Requirements:** Python 3.10 or newer, an internet connection, and a Google Gemini API key.

1. Clone the repository and open the project folder:
   git clone https://github.com/miranda-ruben/Digital-Information.git
   `cd Digital-Information`

2. Install the required dependencies:
   `pip install -r requirements.txt`

3. Copy `.env.example` to `.env` and replace `your_api_key_here` with your Gemini API key.

4. Start the application:
   `python app.py`

5. Open http://127.0.0.1:5000 in your browser and ask an Erasmus-related question.

## Evaluation Across Six Dimensions
Output quality: Assessed against the expected key points of ten predefined Erasmus questions.
Cost per answer: Calculated using token consumption and Gemini pricing.
Response time: Measured through experiment runs, including average latency.
Data requirements and handling: Evaluated based on the official University information supplied to the model and external API usage.
Failure modes: Incomplete answers, unsupported information, invalid citations and API errors; handled through safeguards and user-facing messages.
Vendor lock-in: Dependence on Gemini-specific API functionality and the effort required to migrate to another provider.

## Answer Quality Evaluation

The original Erasmus test questions have been updated to include more specific University of Luxembourg administrative procedures.

The revised questions and their expected key points are available in [`expected_answers.json`](expected_answers.json).

The results of the Gemini answer evaluation, including incomplete answers, unnecessary refusals and identified limitations, are documented in [`gemini_answer_analysis.md`](gemini_answer_analysis.md).

The same ten questions will be used for future testing to evaluate improvements in answer accuracy and completeness.

## Updated Cost Estimate
New model: Gemini-3.5-flash-lite
Development: We used the new free model of Gemini API for the development and testing, as this version is better suited for our project, mostly intended for lightweight tasks, and offers lower estimated API costs. 

Production assumption: For a future production version, we assume paid API usage.

According to Google Cloud pricing, Gemini 3.5 Flash-Lite costs $0.30 per million input tokens and $2.50 per million output tokens at standard global rates.

One action means one student submitting an Erasmus-related question and receiving one AI-generated answer.

Assuming 1,000 input tokens and 3,000 output tokens per action:

Estimated cost per action: $0.0078

Estimated usage: 100 actions per day × 30 days = 3,000 actions per month

Estimated monthly API cost: $23.40

Target users: University of Luxembourg students

Potential customer: University administration. The proposed business model is to offer the service to the university rather than charge students individually.

Conclusion: This new Gemini model is cheaper, potentially faster and more adequate for the idea of UniGuideAI.

## Current MVP Implementation (Technology: Python, Flask, HTML, JavaScript, Gemini API)
The current prototype provides:
•	A web interface where students can ask administrative questions.
•	Integration with the Google Gemini API through a Python Flask backend.
•	Automatic loading of official university documents from .md files.
•	Answers with citations to approved university sources and their last-checked dates.
•	Refusal handling when information is unavailable.
•	Error handling for API rate limits and temporary service failures.

Unlike general-purpose chatbots, UniGuideAI focuses on University of Luxembourg administrative procedures by selecting relevant official university documents and providing answers with source citations.

## Three Known Limitations
1. Limited retrieval precision: The application selects relevant documents using keyword matching but does not retrieve individual passages.
2. No independent deadline validation: Deadlines mentioned in generated answers are not automatically verified against the source documents.
3. No factual citation verification: The application checks that citation URLs are approved, but does not verify that every generated statement is supported by the cited source.

Demo video: https://youtu.be/XVTN6Es4FE8

## Milestone 2

## 1. Two approaches compared
Criterion | Gemini | Groq |
Model tested | `gemini-3.8-flash` | `openai/gpt-oss-120b` |
Request success rate | 10/10 (100%) | 8/10 (80%) |
Average successful-request latency | 24.89 seconds | 7.68 seconds |
Estimated cost for 3,000 actions/month | $36.00 | $5.85 |
Observed failures | Slow responses | Two HTTP 429 rate-limit errors |

## 2. Experiment

`experiment.py` sends ten realistic Erasmus-administration questions to the
gemini model. It records per-case success and latency, then calculates success
rate and average latency in `experiment_answers.json`.


**Result (17 October 2026):** 0/10 cases succeeded (0% success rate) and
average request latency was 0.189s. All ten calls returned HTTP 429
`RESOURCE_EXHAUSTED`: the free-tier daily request quota for this model was
already exhausted. 

**Result (17 October 2026):** 9/10 cases succeeded (90% success rate) and 14.939s. 9 calls were sucessful while one call returned ServerError: 503 UNAVAILABLE due to high demand. 

**Result (19 October 2026):** Gemini API had 10/10 requests succeeded (100%), with an average latency of 24.89 seconds, while GROQ had 8/10 requests succeeded (80%), with an average latency of 7.68 seconds. 

## 3. Chosen approach, three limitations, and what would make you switch
We chose the Gemini Flash API for this project, because we don't have to train the model and it is free. We asked the API already 10 questions in the Experiment above specifically about Erasmus. 


The main limitations are:

**Service availability:** If Google's API is unavailable or the request quota is exhausted, students may not receive an answer.

**Answer accuracy:** The model may generate incorrect information or misunderstand university rules, so answers should be checked against official university sources.

**Provider dependency:** The project depends on Google's API, its pricing, its model availability and its usage limits.

What would make us switch, is an API that doesn't have such a low response quota but at the same time be free, that seems like the biggest issues for us as of right now. 
## 4. Architecture Sketch
(Picture of the drawing that was made)

## 5. First cost estimate

Google Gemini API pricing:
<https://ai.google.dev/gemini-api/docs/pricing>, checked 17 October 2026.
The listed paid rate for Gemini 3.8 Flash through 31 December 2026 is
$0.75 per 1M input tokens and $3.75 per 1M output tokens.

Assumption for one student action: 1,000 input tokens and 3,000 output tokens.

Calculation:
(1,000 × $0.75 / 1,000,000) + (3,000 × $3.75 / 1,000,000)
= $0.00075 + $0.01125
= $0.012 per action


At 100 actions per day for 30 days, the model-only estimate is
3,000 × $0.012 = **$36/month**.

## Plan to the MVP
# MVP Plan

## A. Tasks leading to M3 — MVP

| # | Task | Responsible member | Target date |

| 1 | Finalize MVP scope, user journey, and acceptance criteria | Rayan Essifi | 21 Oct |

| 2 | Select and organize official university sources for the initial use cases | Nelson Costa Alves | 25 Oct |

| 3 | Build the basic application interface and project setup | Ruben Miranda Lopes | 27 Oct |

| 4 | Implement the Gemini prompt and response format for administrative questions | Ruben Miranda Lopes | 30 Oct |

| 5 | Implement the mechanism for providing relevant official information to the AI | Nelson Costa Alves | 2 Nov |

| 6 | Connect the user interface to the AI feature and complete the main user flow | Rayan Essifi | 5 Nov |

| 7 | Test the end-to-end flow using realistic student questions; record bugs | All three | 8 Nov |

| 8 | Fix priority bugs, handle missing or uncertain information, and improve responses | Ruben (AI), Nelson (sources), Rayan (interface/integration) | 11 Nov |

| 9 | Finalize setup instructions, `.env.example`, architecture diagram, and README | Ruben Miranda Lopes | 12 Nov |

| 10 | Verify that the application starts on another team member's laptop | Nelson Costa Alves | 13 Nov |

| 11 | Record the three-minute demo, list known limitations, and prepare M3 summary | All three; Rayan coordinates | 15 Nov |

| 12 | Submit the working MVP, repository link, video, and one-page summary | Team lead | 16 Nov |



