# S TrustLoop Real-Use Validation Report

Generated: 2026-06-21T08:15:37.201102+00:00

## Verdict

**B. Works only as a portfolio prototype, not ready for targeted outreach**

This is a small, self-written validation set. It exposes behavior; it does not prove production reliability.

No evaluator thresholds were changed after these cases were run.

Classification correction: the first runner output was 5 pass, 4 mixed, and 3 fail. Empty expectation lists were incorrectly counted as positive checks for human-good cases. The corrected classification below changes only pass/mixed/fail labels; observed scores, evaluator output, source/output pairs, and human expectations are unchanged.

## Aggregate Results

- Total cases: 12
- Passed: 5
- Mixed: 2
- Failed: 5
- Pass or mixed rate: 58.3%
- Human score-band matches: 9/12
- Missing-topic cases correct: 3/3
- Unsupported-claim cases correct: 4/5
- Contradiction cases correct: 0/2
- Paraphrases underrated: 1
- Lexical false-confidence cases: 0
- Outreach acceptance gate: failed

## Case Results

| Case | Human label | Score | System label | Supported | Weak | Unsupported | Contradicted | Missing | Result |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| case-01-student-policy-summary | good | 78.7 | Mostly grounded | 2 | 2 | 0 | 0 | 3 | mixed |
| case-02-meeting-notes | good | 63.0 | Needs review | 2 | 1 | 2 | 0 | 6 | fail |
| case-03-technical-blog-summary | mixed | 45.4 | Risky | 1 | 0 | 3 | 0 | 7 | pass |
| case-04-health-advice-summary | mixed | 81.2 | Mostly grounded | 2 | 0 | 0 | 0 | 6 | mixed |
| case-05-financial-risk-summary | mixed | 55.6 | Risky | 1 | 1 | 2 | 0 | 6 | pass |
| case-06-legal-policy-summary | mixed | 77.5 | Mostly grounded | 2 | 1 | 0 | 0 | 5 | pass |
| case-07-product-requirements-summary | mixed | 71.6 | Needs review | 3 | 2 | 1 | 0 | 5 | fail |
| case-08-podcast-script | mixed | 48.5 | Risky | 0 | 1 | 3 | 0 | 7 | pass |
| case-09-paraphrased-summary | good | 32.1 | Not reliable | 0 | 0 | 5 | 0 | 7 | fail |
| case-10-subtle-date-error | mixed | 61.6 | Needs review | 1 | 0 | 1 | 0 | 7 | fail |
| case-11-subtle-number-error | mixed | 50.6 | Risky | 0 | 1 | 3 | 0 | 6 | fail |
| case-12-unrelated-answer | bad | 28.8 | Not reliable | 0 | 0 | 2 | 0 | 8 | pass |

## Detailed Findings

### case-01-student-policy-summary: Good grounded student policy summary

- Human label: good
- Expected score band: high
- Observed score: 78.7 (Mostly grounded)
- Result: mixed
- System summary: score matched the human band; 0 claims flagged; 3 topics marked missing.
- Missing topics reported: attendance, late work, privacy
- Human notes: A useful evaluator should treat the four policy claims as supported and avoid inventing coverage gaps.

### case-02-meeting-notes: Good external meeting notes

- Human label: good
- Expected score band: high
- Observed score: 63.0 (Needs review)
- Result: fail
- System summary: score did not match the human band; 2 claims flagged; 6 topics marked missing.
- Missing topics reported: elena, release, lead, neighborhood, app, planning
- Human notes: The decision, owners, dates, requirement, and risk are all grounded in the transcript.

### case-03-technical-blog-summary: Technical summary with an unsupported guarantee

- Human label: mixed
- Expected score band: medium
- Observed score: 45.4 (Risky)
- Result: pass
- System summary: score matched the human band; 3 claims flagged; 7 topics marked missing.
- Missing topics reported: retries, monitoring, jobs, count, failing, small, service
- Human notes: Three claims are grounded. The exactly-once guarantee is invented and should be clearly flagged.

### case-04-health-advice-summary: Incomplete health guidance summary

- Human label: mixed
- Expected score band: medium
- Observed score: 81.2 (Mostly grounded)
- Result: mixed
- System summary: score did not match the human band; 0 claims flagged; 6 topics marked missing.
- Missing topics reported: early care, medication, urgent symptoms, care, mild, skin
- Human notes: The included advice is grounded, but omitting medication cautions and urgent symptoms is meaningful.

### case-05-financial-risk-summary: Financial summary with false safety conclusion

- Human label: mixed
- Expected score band: medium
- Observed score: 55.6 (Risky)
- Result: pass
- System summary: score matched the human band; 2 claims flagged; 6 topics marked missing.
- Missing topics reported: current position, concentration risk, receivables, planned spending, note, current
- Human notes: The factual figures are correct, but the final conclusion reverses the source recommendation and invents a guarantee.

### case-06-legal-policy-summary: Policy summary missing retention and appeal rights

- Human label: mixed
- Expected score band: medium
- Observed score: 77.5 (Mostly grounded)
- Result: pass
- System summary: score matched the human band; 0 claims flagged; 5 topics marked missing.
- Missing topics reported: collection, retention, incident reporting, appeals, email
- Human notes: The output is accurate but materially incomplete because deletion timing and review rights are absent.

### case-07-product-requirements-summary: Product requirements with swapped owners

- Human label: mixed
- Expected score band: medium
- Observed score: 71.6 (Needs review)
- Result: fail
- System summary: score matched the human band; 1 claims flagged; 5 topics marked missing; missed contradiction expectations: Marcus owns the interface design and confirmation messages., Elena owns archive generation, encryption, and link expiration..
- Missing topics reported: user flow, file contents, ownership, launch gate, user
- Human notes: All product requirements are correct except the two owners are swapped. A general detector should not depend on a fixed demo-name list.

### case-08-podcast-script: Oversimplified public-service podcast

- Human label: mixed
- Expected score band: medium
- Observed score: 48.5 (Risky)
- Result: pass
- System summary: score matched the human band; 3 claims flagged; 7 topics marked missing.
- Missing topics reported: purpose, transportation, limitations, privacy, alert, heat, capacity
- Human notes: The podcast covers benefits but omits capacity, coverage, and privacy limitations while making an overbroad access claim.

### case-09-paraphrased-summary: Good strongly paraphrased summary

- Human label: good
- Expected score band: high
- Observed score: 32.1 (Not reliable)
- Result: fail
- System summary: score did not match the human band; 5 claims flagged; 7 topics marked missing.
- Missing topics reported: intake, repair process, records, item, whether, volunteer, category
- Human notes: Every claim preserves the source meaning, but vocabulary is deliberately changed to reveal lexical under-rating.

### case-10-subtle-date-error: Subtle wrong workshop date

- Human label: mixed
- Expected score band: medium
- Observed score: 61.6 (Needs review)
- Result: fail
- System summary: score matched the human band; 1 claims flagged; 7 topics marked missing; missed contradiction expectations: The workshop will take place on July 17 from nine in the morning until three in the afternoon..
- Missing topics reported: followup, cancellation, participants, research, schedule, accepted, receive
- Human notes: Only one date is wrong. A useful review should flag that claim without treating the entire output as unrelated.

### case-11-subtle-number-error: Subtle wrong participant count

- Human label: mixed
- Expected score band: medium
- Observed score: 50.6 (Risky)
- Result: fail
- System summary: score matched the human band; 3 claims flagged; 6 topics marked missing; missed unsupported expectations: The study included twenty participants drawn from students and faculty..
- Missing topics reported: task completion, main finding, recommendation, task, roombooking, completed
- Human notes: The output changes twelve participants to twenty while preserving the rest of the findings.

### case-12-unrelated-answer: Completely unrelated document answer

- Human label: bad
- Expected score band: low
- Observed score: 28.8 (Not reliable)
- Result: pass
- System summary: score matched the human band; 2 claims flagged; 8 topics marked missing.
- Missing topics reported: morning watering, frequency, mulch, rain, watering, morning, water, leaves
- Human notes: The answer is unrelated to the gardening source and should be unsupported. The separate live Q&A path should abstain before creating such an answer.

## Top 5 Failure Modes

- Noisy missing-topic labels in human-good outputs: 16
- Expected contradictions missed: 3
- Human score bands missed: 3
- Expected unsupported claims missed: 1
- Good paraphrases underrated: 1

## Top 5 Things the Prototype Does Well

- Completed the same manual-audit pipeline for all 12 external outputs.
- Matched the human score band in 9 of 12 cases.
- Detected all expected missing topics in 3 of 3 omission cases.
- Flagged all expected unsupported claims in 4 of 5 hallucination cases.
- Clearly rejected the unrelated answer with a score of 28.8 and 2 unsupported claims.

## Acceptance-Gate Interpretation

Outreach readiness requires at least 70% pass-or-mixed cases, complete detection of the labeled unsupported claims, meaningful detection of the labeled omissions, and clear rejection of the unrelated answer.

The measured gate **did not pass**.

The lexical design should be discussed openly: semantically correct paraphrases can score too low, while outputs that repeat source vocabulary can retain too much confidence despite a changed conclusion or detail.
