# MatchWhy — Ranking & Plain-Language Reasons with an Eval Harness

A full-stack companion to JobSense. MatchWhy consumes candidate postings from JobSense (or demo data), scores them against a person's stated preferences, applies hard constraints and diversity rules, explains each recommendation using only the posting and stated preferences, and closes the loop with feedback and evaluation.

## Quick start
1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open http://localhost:5174 (UI), http://localhost:8001/docs (API).

The demo starts with a sample profile and a small posting corpus. Set `JOBSENSE_API_URL=http://host.docker.internal:8000` to fetch candidates from a locally running JobSense API (or set the service URL appropriate to your environment). The demo source is used when JobSense is unavailable.

## What is implemented
- Candidate ingestion from JobSense API with a local fallback dataset.
- Fit ranking: retrieval relevance, explicit constraint checks, seniority alignment, responsibility-scope alignment, freshness and skill overlap.
- Hard constraints can exclude jobs (e.g. location or level); exclusions are visible in the API ranking audit.
- Diversity-aware selection limits repeated companies and near-duplicate role titles.
- One-sentence match reasons grounded in posting text and profile preferences. The fallback reason generator is deterministic; optional LLM generation is constrained to supplied facts and can be configured with an OpenAI-compatible endpoint.
- Human feedback: `good`, `wrong_job`, `weak_reason`.
- Quality dashboard: feedback grouped into wrong level, ignored constraint, generic reason, and other.
- Weekly improvement suggestions generated from feedback clusters.
- Evaluation dataset of person/job pairs, Precision@K and nDCG@K.
- Optional LLM-as-judge scoring for truthfulness, specificity and preference alignment; human spot-check samples are exported.
- CI regression gate compares metrics against committed thresholds.

## Environment
See `.env.example`. If an LLM key is absent, the judge uses transparent heuristic scoring and the reason generator uses grounded deterministic templates. This keeps the app runnable without paid API credentials. Configure `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `LLM_MODEL` to enable model-based judge and reasons.

## API overview
- `GET /api/profile` — current demo profile
- `PUT /api/profile` — update preferences
- `POST /api/recommendations/refresh` — refresh candidates and rank
- `GET /api/recommendations` — ranked recommendations
- `POST /api/feedback` — submit match feedback
- `GET /api/quality` — feedback dashboard and weekly fixes
- `POST /api/evaluation/run` — run ranking evaluation and CI-style gate
- `GET /health` — health check

## Evaluation
Run locally:
```bash
cd backend
pip install -r requirements.txt
pytest
python -m app.evaluate_cli
```
The checked-in `eval/labelled_pairs.json` is a starter labelled set. Replace/expand it with consented and reviewed labels before making performance claims. The CI gate intentionally fails if precision@5 or nDCG@5 falls below `eval/thresholds.json`.

## Production checklist
Add authentication and per-user data isolation, migrations, audit retention, rate limiting, real human-reviewed labels, secure secrets, monitoring, and explicit consent/data deletion. LLM-as-judge is a diagnostic signal, not ground truth; maintain human spot checks.
