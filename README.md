# UniGuide AI: Milestone 2 
https://github.com/miranda-ruben/Digital-Information (Public)
**Chosen approach:** Gemini API, `gemini-3.8-flash`

## 1. Experiment

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

## 2. First cost estimate

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