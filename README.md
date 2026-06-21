# S TrustLoop

## Overview

S TrustLoop is a zero-budget, local-first portfolio prototype for reviewing generated summaries, quizzes, podcast scripts, meeting notes, document answers, and work reports against source text.

It demonstrates a transparent review workflow: split an output into claims, retrieve lexically similar source chunks, apply simple support and contradiction rules, surface missing topics, calculate heuristic review signals, and collect human feedback.

> S TrustLoop is an independent prototype. It is not affiliated with, endorsed by, or integrated with any commercial voice-AI platform.

## What S TrustLoop Is and Is Not

S TrustLoop is a local-first portfolio prototype for exploring how AI-generated outputs can be reviewed against source text.

It uses deterministic generation, lexical claim-to-source matching, missing-topic detection, simple contradiction heuristics, feedback capture, and visual trust cards.

It does not use an LLM, semantic embeddings, vector search, model training, or production-grade factuality checking. It is not production-ready or enterprise-ready.

The scores are review indicators for the demo workflow. They are not proof that an output is factually correct.

## Destructive Demo-Data Warning

`POST /api/demo/seed` and `DELETE /api/demo/reset` replace the contents of the local prototype database. This includes uploaded documents.

Do not use demo seed/reset with important files. Treat this as a private localhost prototype with disposable data.

The frontend asks for confirmation before user-triggered replacement. Direct API calls remain destructive.

## Current Features

- Ten synthetic source documents and three deliberately incorrect negative-test outputs
- TXT, Markdown, PDF, and DOCX upload
- Deterministic local generation for summaries, key points, quizzes, podcast scripts, meeting notes, work reports, and document Q&A
- Lexical claim-to-source retrieval
- Supported, weakly supported, unsupported, and contradicted review states
- Source-overlap, coverage, evidence-availability, readability, and flagged-claim indicators
- Heading and term-based missing-topic detection
- Simple date, owner, and negated-requirement contradiction rules
- Human feedback storage and aggregate feedback analytics
- Demo topic-memory signals and recap prompts
- Browser speech synthesis for output preview
- Three guided demo flows
- Manual audit mode for externally generated outputs

## Architecture

```text
Next.js UI
   |
FastAPI routes
   |
   +-- document parser -> section-aware chunks -> SQLite
   +-- deterministic output templates
   +-- claim splitter -> lexical retrieval -> simple contradiction rules
   +-- topic coverage -> transparent heuristic scoring
   +-- feedback storage -> aggregate analytics + demo topic signals
```

The live path does not download or call a model. Retrieval is lexical. There is no embedding model or vector database.

See [docs/architecture.md](docs/architecture.md).

## Stack

- Next.js, TypeScript, Tailwind CSS, Recharts
- FastAPI, SQLAlchemy, SQLite, Pydantic
- PyMuPDF and python-docx for local parsing
- Browser SpeechSynthesis API
- Pytest

No paid AI, voice, or cloud API is required.

## Trust-Score Methodology

The current score is a fixed heuristic:

```text
35% lexical claim support
25% source-topic coverage
15% retrieved-evidence availability
10% readability and structure
10% fixed neutral feedback prior
 5% output-format checks
```

Feedback is stored and shown in analytics. It does not currently change an existing trust score or train a model.

See:

- [Trust score methodology](docs/trust-score-methodology.md)
- [Limitations and production roadmap](docs/limitations-and-production-roadmap.md)

## Data Model

SQLite stores:

- users
- documents and document chunks
- generated outputs
- evaluation runs
- claim checks and retrieved source text
- missing-topic rows
- user feedback
- demo learning-memory rows

Tests use a separate temporary SQLite database and do not reset the normal development database.

## API

Key routes:

- `GET /health`
- `POST /api/demo/seed`
- `DELETE /api/demo/reset`
- `POST /api/audit/manual`
- `GET /api/documents`
- `POST /api/documents/upload`
- `DELETE /api/documents/{document_id}`
- `POST /api/generate/{output-type}`
- `POST /api/ask`
- `POST /api/evaluate/{output_id}`
- `GET /api/outputs/{output_id}/trust-card`
- `GET /api/outputs/{output_id}/claims`
- `GET /api/outputs/{output_id}/missing-topics`
- `POST /api/feedback`
- `GET /api/learning-memory/{user_id}`
- `GET /api/analytics/overview`

FastAPI exposes the interactive schema at `http://localhost:8000/docs`.

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Verification

```bash
cd backend
python -m pytest

cd ../frontend
npm run build
npm audit
```

The previous interactive `next lint` script was removed because ESLint is not configured. The production build still performs TypeScript validation.

## Demo Flows

1. **Student review:** generate a summary, inspect source overlap and coverage gaps, then open the demo topic signals.
2. **Meeting notes:** generate structured notes, inspect retrieved evidence, then open the curated wrong-notes example.
3. **Work report:** generate a deterministic report, inspect flagged claims, and open aggregate review analytics.

The negative tests are synthetic and intentionally easy to detect. They demonstrate the interface and rule behavior; they do not prove generalization.

See [docs/demo-script.md](docs/demo-script.md).

## Real-Use Validation

S TrustLoop includes a small real-use validation set under [`demo-data/real-use-validation`](demo-data/real-use-validation).

The set contains twelve self-written, non-sensitive source/output pairs with human-written expected behavior labels. It includes grounded outputs, paraphrases, omissions, unsupported claims, wrong dates, wrong numbers, swapped owners, an oversimplified podcast, and an unrelated answer.

It is designed to expose limitations, not to prove production reliability.

Current verdict: **B. Works only as a portfolio prototype, not ready for targeted outreach.**

Corrected results after fixing a validation-runner classification bug:

- 5 passed
- 2 mixed
- 5 failed
- 58.3% pass-or-mixed
- 0 of 2 expected contradiction cases detected
- 1 good paraphrase severely underrated

No evaluator thresholds or human labels were changed after observing the results. See the complete [real-use validation report](docs/validation/real-use-validation-report.md).

## Screenshots

Screenshots in [docs/screenshots](docs/screenshots) were captured from a live seeded run. They predate the V1.0.1 wording cleanup, so the layout and scores remain representative while some labels differ from the current interface.

## Honest Portfolio Positioning

> Built S TrustLoop, a local-first portfolio prototype that uses deterministic generation, lexical source matching, missing-topic checks, simple contradiction rules, feedback capture, and a Next.js review interface to explore how generated outputs could be made more inspectable.

This is a demo-ready portfolio prototype, not a production factuality service.
