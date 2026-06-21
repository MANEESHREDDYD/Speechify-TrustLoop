# Architecture

S TrustLoop is an independent, local-first portfolio prototype with a Next.js interface and FastAPI service.

```text
Document -> parser -> chunks -> deterministic generator
                         |              |
                         +-> retrieval <-+
                                |
Output -> claims -> lexical matching -> heuristic scores
                                      -> feedback storage
                                      -> aggregate analytics + demo topic signals

Pasted external output -> manual audit document/output -> same evaluation path
```

SQLite stores documents, chunks, outputs, evaluation runs, claim checks, missing topics, feedback, and demo learning-memory rows. The live path requires no remote model or paid API.

The generator is deterministic. Retrieval is lexical, not semantic. There is no embedding model, vector database, model training, or event-driven analytics pipeline.

Demo seed/reset replaces all local database contents. Tests override `DATABASE_URL` before importing the application and use a disposable temporary SQLite database.

Document deletion explicitly removes dependent chunks, outputs, evaluations, claim checks, missing-topic rows, and output feedback. Demo learning-memory rows are user-level aggregates and are not precisely attributable to one document.

Manual audit stores pasted source text and pasted external output with `generation_mode=external_manual`. It never calls the deterministic generator.
