from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

_RUNTIME_TEMP_DIRECTORY = None
if __name__ == "__main__":
    explicit_validation_url = os.getenv("VALIDATION_DATABASE_URL")
    if explicit_validation_url:
        os.environ["DATABASE_URL"] = explicit_validation_url
    else:
        _RUNTIME_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="s-trustloop-validation-")
        validation_db = Path(_RUNTIME_TEMP_DIRECTORY.name) / "validation.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{validation_db.as_posix()}"


from app.database import SessionLocal, engine, init_db
from app.services.manual_audit import run_manual_audit
from app.utils.text_utils import words


DEFAULT_VALIDATION_DIR = REPO_ROOT / "demo-data" / "real-use-validation"
DEFAULT_RESULTS_PATH = REPO_ROOT / "docs" / "validation" / "real-use-validation-results.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "validation" / "real-use-validation-report.md"

SCORE_BANDS = {
    "high": lambda score: score >= 75,
    "medium": lambda score: 40 <= score < 80,
    "low": lambda score: score < 60,
}


def _text_match(expected: str, actual: str) -> bool:
    expected_lower = expected.lower()
    actual_lower = actual.lower()
    if expected_lower in actual_lower or actual_lower in expected_lower:
        return True
    expected_terms = set(words(expected))
    actual_terms = set(words(actual))
    return bool(expected_terms) and len(expected_terms & actual_terms) / len(expected_terms) >= 0.45


def _all_expected_match(expected: list[str], actual: list[str]) -> tuple[bool, list[str]]:
    missed = [
        item
        for item in expected
        if not any(_text_match(item, candidate) for candidate in actual)
    ]
    return not missed, missed


def _classify_case(
    *,
    expectation: dict,
    score_match: bool,
    missing_match: bool,
    unsupported_match: bool,
    contradiction_match: bool,
    flagged_count: int,
    missing_count: int,
) -> str:
    if expectation["human_label"] == "good":
        if score_match and missing_match and flagged_count <= 1 and missing_count <= 2:
            return "pass"
        if score_match or (flagged_count <= 1 and missing_count <= 2):
            return "mixed"
        return "fail"

    critical_expected = bool(
        expectation["expected_unsupported_claims"]
        or expectation["expected_contradictions"]
    )
    critical_match = unsupported_match and contradiction_match
    if critical_expected and not critical_match:
        return "fail"

    checks = [score_match, missing_match, unsupported_match, contradiction_match]
    if all(checks):
        return "pass"
    if sum(checks) >= 2:
        return "mixed"
    return "fail"


def _case_result(case_dir: Path, session) -> dict:
    source_text = (case_dir / "source.txt").read_text(encoding="utf-8")
    generated_text = (case_dir / "output.txt").read_text(encoding="utf-8")
    expectation = json.loads((case_dir / "expected_behavior.json").read_text(encoding="utf-8"))

    audit = run_manual_audit(
        session,
        user_id="validation-user",
        source_title=expectation["case_name"],
        source_text=source_text,
        output_type=expectation["output_type"],
        generated_text=generated_text,
    )
    card = audit["trust_card"]
    claims = audit["claim_checks"]
    topics = [item["topic"] for item in audit["missing_topics"]]
    flagged_claims = [
        item["claim_text"]
        for item in claims
        if item["status"] in {"unsupported", "contradicted"}
    ]
    contradicted_claims = [
        item["claim_text"]
        for item in claims
        if item["status"] == "contradicted"
    ]

    score_match = SCORE_BANDS[expectation["expected_score_band"]](card["trust_score"])
    missing_match, missed_topics = _all_expected_match(
        expectation["expected_missing_topics"], topics
    )
    unsupported_match, missed_unsupported = _all_expected_match(
        expectation["expected_unsupported_claims"], flagged_claims
    )
    contradiction_match, missed_contradictions = _all_expected_match(
        expectation["expected_contradictions"], contradicted_claims
    )
    status = _classify_case(
        expectation=expectation,
        score_match=score_match,
        missing_match=missing_match,
        unsupported_match=unsupported_match,
        contradiction_match=contradiction_match,
        flagged_count=card["unsupported_claims"] + card["contradicted_claims"],
        missing_count=len(topics),
    )
    paraphrase_underrated = bool(
        expectation.get("paraphrase_case")
        and expectation["human_label"] == "good"
        and card["trust_score"] < 75
    )
    lexical_false_confidence = bool(
        expectation["human_label"] in {"mixed", "bad"}
        and card["trust_score"] >= 75
        and (missed_unsupported or missed_contradictions)
    )

    summary_parts = [
        f"score {'matched' if score_match else 'did not match'} the human band",
        f"{len(flagged_claims)} claims flagged",
        f"{len(topics)} topics marked missing",
    ]
    if missed_unsupported:
        summary_parts.append(f"missed unsupported expectations: {', '.join(missed_unsupported)}")
    if missed_contradictions:
        summary_parts.append(f"missed contradiction expectations: {', '.join(missed_contradictions)}")
    if missed_topics:
        summary_parts.append(f"missed topic expectations: {', '.join(missed_topics)}")

    return {
        "case_id": case_dir.name,
        "case_name": expectation["case_name"],
        "output_type": expectation["output_type"],
        "trust_score": card["trust_score"],
        "label": card["label"],
        "supported_claims": card["supported_claims"],
        "weakly_supported_claims": card["weakly_supported_claims"],
        "unsupported_claims": card["unsupported_claims"],
        "contradicted_claims": card["contradicted_claims"],
        "missing_topics": topics,
        "expected_missing_topics": expectation["expected_missing_topics"],
        "expected_unsupported_claims": expectation["expected_unsupported_claims"],
        "expected_contradictions": expectation["expected_contradictions"],
        "human_label": expectation["human_label"],
        "expected_score_band": expectation["expected_score_band"],
        "score_matched_human_expectation": score_match,
        "missing_topics_correctly_detected": missing_match,
        "unsupported_claims_correctly_detected": unsupported_match,
        "contradictions_correctly_detected": contradiction_match,
        "missed_expected_topics": missed_topics,
        "missed_expected_unsupported_claims": missed_unsupported,
        "missed_expected_contradictions": missed_contradictions,
        "paraphrase_underrated": paraphrase_underrated,
        "lexical_overlap_false_confidence": lexical_false_confidence,
        "system_result_summary": "; ".join(summary_parts) + ".",
        "result": status,
        "notes": expectation["notes"],
        "document_id": audit["document_id"],
        "output_id": audit["output_id"],
        "evaluation_id": audit["evaluation_id"],
    }


def _aggregate(results: list[dict]) -> dict:
    result_counts = Counter(item["result"] for item in results)
    expected_missing_cases = [item for item in results if item["expected_missing_topics"]]
    expected_unsupported_cases = [item for item in results if item["expected_unsupported_claims"]]
    expected_contradiction_cases = [item for item in results if item["expected_contradictions"]]

    metrics = {
        "total_cases": len(results),
        "passed_cases": result_counts["pass"],
        "mixed_cases": result_counts["mixed"],
        "failed_cases": result_counts["fail"],
        "score_matched_human_expectation": sum(item["score_matched_human_expectation"] for item in results),
        "missing_topic_cases_correct": sum(item["missing_topics_correctly_detected"] for item in expected_missing_cases),
        "missing_topic_cases_total": len(expected_missing_cases),
        "unsupported_claim_cases_correct": sum(item["unsupported_claims_correctly_detected"] for item in expected_unsupported_cases),
        "unsupported_claim_cases_total": len(expected_unsupported_cases),
        "contradiction_cases_correct": sum(item["contradictions_correctly_detected"] for item in expected_contradiction_cases),
        "contradiction_cases_total": len(expected_contradiction_cases),
        "paraphrase_underrated_cases": sum(item["paraphrase_underrated"] for item in results),
        "lexical_false_confidence_cases": sum(item["lexical_overlap_false_confidence"] for item in results),
    }

    unrelated = next(item for item in results if item["case_id"] == "case-12-unrelated-answer")
    pass_or_mixed = metrics["passed_cases"] + metrics["mixed_cases"]
    support_gate = (
        metrics["unsupported_claim_cases_correct"] == metrics["unsupported_claim_cases_total"]
        and metrics["unsupported_claim_cases_total"] > 0
    )
    missing_gate = (
        metrics["missing_topic_cases_correct"] == metrics["missing_topic_cases_total"]
        and metrics["missing_topic_cases_total"] > 0
    )
    unrelated_gate = unrelated["unsupported_claims_correctly_detected"]
    outreach_gate = (
        pass_or_mixed / max(1, metrics["total_cases"]) >= 0.70
        and support_gate
        and missing_gate
        and unrelated_gate
    )

    if outreach_gate:
        verdict = "A"
        verdict_text = "Works well enough for honest outreach demo"
    elif pass_or_mixed / max(1, metrics["total_cases"]) >= 0.50:
        verdict = "B"
        verdict_text = "Works only as a portfolio prototype, not ready for targeted outreach"
    else:
        verdict = "C"
        verdict_text = "Fails real-use validation; needs technical rebuild before outreach"

    failure_counts = Counter({
        "Noisy missing-topic labels in human-good outputs": sum(
            len(item["missing_topics"]) for item in results if item["human_label"] == "good"
        ),
        "Expected contradictions missed": sum(len(item["missed_expected_contradictions"]) for item in results),
        "Expected unsupported claims missed": sum(len(item["missed_expected_unsupported_claims"]) for item in results),
        "Expected missing topics missed": sum(len(item["missed_expected_topics"]) for item in results),
        "Human score bands missed": sum(not item["score_matched_human_expectation"] for item in results),
        "Good paraphrases underrated": metrics["paraphrase_underrated_cases"],
        "Lexical overlap produced false confidence": metrics["lexical_false_confidence_cases"],
    })
    top_failures = [
        {"failure_mode": name, "count": count}
        for name, count in failure_counts.most_common(5)
    ]
    strengths = [
        f"Completed the same manual-audit pipeline for all {metrics['total_cases']} external outputs.",
        f"Matched the human score band in {metrics['score_matched_human_expectation']} of {metrics['total_cases']} cases.",
        f"Detected all expected missing topics in {metrics['missing_topic_cases_correct']} of {metrics['missing_topic_cases_total']} omission cases.",
        f"Flagged all expected unsupported claims in {metrics['unsupported_claim_cases_correct']} of {metrics['unsupported_claim_cases_total']} hallucination cases.",
        f"Clearly rejected the unrelated answer with a score of {unrelated['trust_score']} and {unrelated['unsupported_claims']} unsupported claims.",
    ]
    return {
        **metrics,
        "pass_or_mixed_rate": round(pass_or_mixed / max(1, metrics["total_cases"]), 3),
        "outreach_acceptance_gate_passed": outreach_gate,
        "verdict": verdict,
        "verdict_text": verdict_text,
        "top_5_failure_modes": top_failures,
        "top_5_strengths": strengths,
    }


def _markdown_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# S TrustLoop Real-Use Validation Report",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Verdict",
        "",
        f"**{summary['verdict']}. {summary['verdict_text']}**",
        "",
        "This is a small, self-written validation set. It exposes behavior; it does not prove production reliability.",
        "",
        "No evaluator thresholds were changed after these cases were run.",
        "",
        "Classification correction: the first runner output was 5 pass, 4 mixed, and 3 fail. Empty expectation lists were incorrectly counted as positive checks for human-good cases. The corrected classification below changes only pass/mixed/fail labels; observed scores, evaluator output, source/output pairs, and human expectations are unchanged.",
        "",
        "## Aggregate Results",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Passed: {summary['passed_cases']}",
        f"- Mixed: {summary['mixed_cases']}",
        f"- Failed: {summary['failed_cases']}",
        f"- Pass or mixed rate: {summary['pass_or_mixed_rate']:.1%}",
        f"- Human score-band matches: {summary['score_matched_human_expectation']}/{summary['total_cases']}",
        f"- Missing-topic cases correct: {summary['missing_topic_cases_correct']}/{summary['missing_topic_cases_total']}",
        f"- Unsupported-claim cases correct: {summary['unsupported_claim_cases_correct']}/{summary['unsupported_claim_cases_total']}",
        f"- Contradiction cases correct: {summary['contradiction_cases_correct']}/{summary['contradiction_cases_total']}",
        f"- Paraphrases underrated: {summary['paraphrase_underrated_cases']}",
        f"- Lexical false-confidence cases: {summary['lexical_false_confidence_cases']}",
        f"- Outreach acceptance gate: {'passed' if summary['outreach_acceptance_gate_passed'] else 'failed'}",
        "",
        "## Case Results",
        "",
        "| Case | Human label | Score | System label | Supported | Weak | Unsupported | Contradicted | Missing | Result |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["cases"]:
        lines.append(
            f"| {item['case_id']} | {item['human_label']} | {item['trust_score']} | "
            f"{item['label']} | {item['supported_claims']} | {item['weakly_supported_claims']} | "
            f"{item['unsupported_claims']} | {item['contradicted_claims']} | "
            f"{len(item['missing_topics'])} | {item['result']} |"
        )

    lines.extend(["", "## Detailed Findings", ""])
    for item in payload["cases"]:
        lines.extend([
            f"### {item['case_id']}: {item['case_name']}",
            "",
            f"- Human label: {item['human_label']}",
            f"- Expected score band: {item['expected_score_band']}",
            f"- Observed score: {item['trust_score']} ({item['label']})",
            f"- Result: {item['result']}",
            f"- System summary: {item['system_result_summary']}",
            f"- Missing topics reported: {', '.join(item['missing_topics']) or 'none'}",
            f"- Human notes: {item['notes']}",
            "",
        ])

    lines.extend(["## Top 5 Failure Modes", ""])
    for item in summary["top_5_failure_modes"]:
        lines.append(f"- {item['failure_mode']}: {item['count']}")
    lines.extend(["", "## Top 5 Things the Prototype Does Well", ""])
    for item in summary["top_5_strengths"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Acceptance-Gate Interpretation",
        "",
        "Outreach readiness requires at least 70% pass-or-mixed cases, complete detection of the labeled unsupported claims, meaningful detection of the labeled omissions, and clear rejection of the unrelated answer.",
        "",
        f"The measured gate **{'passed' if summary['outreach_acceptance_gate_passed'] else 'did not pass'}**.",
        "",
        "The lexical design should be discussed openly: semantically correct paraphrases can score too low, while outputs that repeat source vocabulary can retain too much confidence despite a changed conclusion or detail.",
    ])
    return "\n".join(lines) + "\n"


def run_validation(
    *,
    validation_dir: Path = DEFAULT_VALIDATION_DIR,
    results_path: Path = DEFAULT_RESULTS_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> dict:
    case_dirs = sorted(
        path for path in validation_dir.iterdir()
        if path.is_dir() and path.name.startswith("case-")
    )
    if len(case_dirs) < 12:
        raise ValueError(f"Expected at least 12 validation cases, found {len(case_dirs)}")

    init_db()
    with SessionLocal() as session:
        results = [_case_result(case_dir, session) for case_dir in case_dirs]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation_set": str(validation_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "threshold_note": "Human labels and score bands were committed before the first validation run. Evaluator thresholds were not tuned after observing results.",
        "first_run_before_classification_bug_fix": {
            "passed_cases": 5,
            "mixed_cases": 4,
            "failed_cases": 3,
            "verdict": "B",
            "note": "A runner-classification bug gave human-good cases credit for empty expectation lists. The evaluator scores and human labels were not changed.",
        },
        "summary": _aggregate(results),
        "cases": results,
    }
    results_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    return payload


def main() -> int:
    try:
        payload = run_validation()
        summary = payload["summary"]
        print(
            f"Validated {summary['total_cases']} cases: "
            f"{summary['passed_cases']} pass, {summary['mixed_cases']} mixed, "
            f"{summary['failed_cases']} fail."
        )
        print(f"Verdict: {summary['verdict']}. {summary['verdict_text']}")
        return 0
    finally:
        engine.dispose()
        if _RUNTIME_TEMP_DIRECTORY is not None:
            _RUNTIME_TEMP_DIRECTORY.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
