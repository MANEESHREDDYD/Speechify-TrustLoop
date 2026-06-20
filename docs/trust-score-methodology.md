# Trust Score Methodology

S TrustLoop exposes a transparent composite score rather than a black-box confidence number.

- Grounding (35%): supported claims plus half credit for weak support.
- Coverage (25%): important source topics represented in the output.
- Citation quality (15%): claims with a plausible supporting source chunk.
- Readability (10%): clear structure and manageable sentence length.
- User feedback (10%): neutral until feedback is collected.
- Task fit (5%): action-item quality for meetings or question relevance for quizzes.

Contradicted and unsupported claims separately increase hallucination risk. Scores are heuristics for prioritizing human review, not proof of factual correctness.
