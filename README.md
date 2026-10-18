# UniGuide AI: Milestone 2 
https://github.com/miranda-ruben/Digital-Information (Public)
**Chosen approach:** Gemini API, `gemini-3.8-flash`

## 1. Two approaches compared


## 2. Experiment

`experiment.py` sends ten realistic Erasmus-administration questions to the
gemini model. It records per-case success and latency, then calculates success
rate and average latency in `experiment_results.json`.

Run it with:

```powershell
python experiment.py
```

**Result (17 October 2026):** 0/10 cases succeeded (0% success rate) and
average request latency was 0.189s. All ten calls returned HTTP 429
`RESOURCE_EXHAUSTED`: the free-tier daily request quota for this model was
already exhausted. 

**Result (17 October 2026):** 9/10 cases succeeded (90% success rate) and 14.939s. 9 calls were sucessful while one call returned ServerError: 503 UNAVAILABLE due to high demand. 


## 3. Chosen approach, three limitations, and what would make you switch
We chose the Gemini Flash API for this project, because we don't have to train the model and it is free. We asked the API already 10 questions in the Experiment above specifically about Erasmus. 

The main limitations are:

**Service availability:** If Google's API is unavailable or the request quota is exhausted, students may not receive an answer.

**Answer accuracy:** The model may generate incorrect information or misunderstand university rules, so answers should be checked against official university sources.

**Provider dependency:** The project depends on Google's API, its pricing, its model availability and its usage limits.

What would make us switch, is an API that doesn't have such a low response quota but at the same time be free, that seems like the biggest issues for us as of right now. 
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

<https://ai.google.dev/gemini-api/docs/pricing>, checked 17 October 2026.