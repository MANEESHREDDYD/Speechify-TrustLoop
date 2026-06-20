# Limitations and Production Roadmap

## Current Limitations

- Localhost-only portfolio prototype.
- No authentication or authorization.
- Single demo-user flow.
- No production-safe upload pipeline.
- Demo seed/reset can wipe local demo data and uploaded documents.
- No LLM generation.
- No Ollama integration.
- No semantic embeddings or vector database.
- Retrieval is lexical.
- Claim support is based on source-text overlap, not formal factual proof.
- Contradiction detection is heuristic and limited.
- Feedback is stored and shown in analytics but does not retrain a model.
- Feedback does not currently change existing trust scores.
- Learning memory is a demo signal, not measured learning.
- Learning-memory rows cannot be precisely attributed to one deleted document and may remain stale until recomputed.
- Demo data is synthetic and curated.
- Scores do not prove generalization.
- PDF page boundaries are not preserved in evidence chunks.
- TXT and Markdown page numbers are approximate chunk-position labels.
- There is no upload size limit, MIME validation, malware scanning, or hardened parser sandbox.
- Analytics aggregate database state rather than a real event stream.
- The frontend has limited API error handling and no automated browser tests.

## Production Roadmap

1. Isolated user accounts and document ownership.
2. Upload limits, MIME validation, malware scanning, and safer file parsing.
3. Database migrations and enforced foreign keys/cascades.
4. Real event logging for analytics.
5. Manual audit mode for external AI outputs.
6. Semantic retrieval with documented fallback.
7. Cross-encoder or NLI-based claim verification.
8. Larger labeled benchmark with paraphrases, omissions, numbers, dates, and adversarial cases.
9. Human review queues for low-trust outputs.
10. Feedback-calibrated scoring.
11. Real quiz attempts and learning outcomes.
12. Frontend error states and automated browser tests.

Roadmap items are not implemented features.
