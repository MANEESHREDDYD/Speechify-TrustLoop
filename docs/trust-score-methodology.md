# Trust Score Methodology

S TrustLoop exposes a transparent heuristic review score rather than a black-box confidence number.

- Source overlap (35%): lexically supported claims plus half credit for weak matches.
- Coverage (25%): important source topics represented in the output.
- Evidence availability (15%): claims with a retrieved source chunk ID.
- Readability (10%): clear structure and manageable sentence length.
- Feedback prior (10%): currently fixed at a neutral `0.75`; collected feedback does not change this score.
- Format check (5%): required output markers such as an action-item table or quiz answer labels.

Unsupported and rule-contradicted claims increase the displayed flagged-claim risk. The contradiction rules cover limited date, owner-name, and negated-requirement patterns.

The score does not measure citation correctness, semantic entailment, quiz relevance, learner understanding, or production factuality. Re-evaluating an output creates another evaluation row, so aggregate analytics can count repeated evaluations.
