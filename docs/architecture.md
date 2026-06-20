# Architecture

S TrustLoop is an independent, local-first monorepo with a Next.js interface and FastAPI service.

```text
Document -> parser -> chunks -> deterministic generator
                         |              |
                         +-> retrieval <-+
                                |
Output -> claims -> evidence matching -> scores -> feedback/memory/analytics
```

SQLite stores documents, chunks, outputs, evaluation runs, claim evidence, missing topics, feedback, learning memory, and analytics events. The core path requires no remote model or paid API.
