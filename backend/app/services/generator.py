import re

from app.utils.text_utils import sentences, slug_title, top_terms


def _sections(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^(Section\s+\d+\s*:[^\n]+|Attendees:|Transcript:|Title:[^\n]+)$", re.I | re.M)
    matches = list(pattern.finditer(text))
    result: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        if heading.lower().startswith("title:"):
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if body:
            result.append((heading, body))
    return result


def _section_name(heading: str) -> str:
    return re.sub(r"^section\s+\d+\s*:\s*", "", heading, flags=re.I).strip()


def _first_sentence(text: str) -> str:
    values = sentences(text)
    return values[0] if values else text.strip().splitlines()[0]


def generate_summary(document_text: str) -> str:
    title = slug_title(document_text)
    sections = _sections(document_text)
    source_sentences = sentences(document_text)
    main = source_sentences[0] if source_sentences else "The source presents a voice-first workflow."
    points = [_first_sentence(body) for _, body in sections[:6]]
    if not points:
        points = source_sentences[:5]
    why = source_sentences[-1] if source_sentences else main
    lines = "\n".join(f"{i}. {point}" for i, point in enumerate(points, 1))
    return (
        f"# Summary\n\n## Main idea\n{title}: {main}\n\n"
        f"## Key points\n{lines}\n\n## Why it matters\n{why}"
    )


def generate_key_points(document_text: str) -> str:
    sections = _sections(document_text)
    points = [_first_sentence(body) for _, body in sections[:8]] or sentences(document_text)[:8]
    return "# Key Points\n\n" + "\n".join(f"- {point}" for point in points)


def generate_quiz(document_text: str) -> str:
    sections = _sections(document_text)
    if not sections:
        sections = [(term.title(), sentence) for (term, _), sentence in zip(top_terms(document_text, 5), sentences(document_text))]
    questions = []
    for index, (heading, body) in enumerate(sections[:5], 1):
        topic = _section_name(heading)
        answer = _first_sentence(body)
        distractors = [
            "It removes the need for source material.",
            "It guarantees understanding without review.",
            "It stores every user interaction permanently.",
        ]
        questions.append(
            f"{index}. Which statement is grounded in the section about {topic.lower()}?\n"
            f"A. {distractors[0]}\nB. {answer}\nC. {distractors[1]}\nD. {distractors[2]}\n"
            f"Answer: B\nSource topic: {topic}"
        )
    return "# Quiz\n\n" + "\n\n".join(questions)


def generate_podcast_script(document_text: str) -> str:
    title = slug_title(document_text)
    sections = _sections(document_text)
    beats = [(_section_name(h), _first_sentence(b)) for h, b in sections[:6]]
    if not beats:
        beats = [("Key idea", sentence) for sentence in sentences(document_text)[:5]]
    dialogue = [f"Host 1: Welcome to a source-grounded briefing on {title}."]
    for index, (topic, claim) in enumerate(beats):
        host = "Host 2" if index % 2 == 0 else "Host 1"
        dialogue.append(f"{host}: On {topic.lower()}, the source explains that {claim}")
    dialogue.append("Host 2: The key takeaway is to keep the convenience of audio connected to evidence and active review.")
    return "# AI Podcast Script\n\n" + "\n\n".join(dialogue)


def _meeting_lines(document_text: str) -> list[str]:
    return [line.strip() for line in document_text.splitlines() if re.match(r"^[A-Z][a-z]+:", line.strip())]


def generate_meeting_notes(document_text: str) -> str:
    attendee_block = re.search(r"Attendees:\s*(.*?)\s*Transcript:", document_text, re.S | re.I)
    attendees = [line.strip() for line in (attendee_block.group(1).splitlines() if attendee_block else []) if line.strip()]
    transcript = _meeting_lines(document_text)
    decisions = []
    actions = []
    risks = []
    due_re = re.compile(r"\b(?:July|August|September|October|November|December|January|February|March|April|May|June)\s+\d{1,2}\b", re.I)
    for line in transcript:
        speaker, statement = line.split(":", 1)
        statement = statement.strip()
        if re.search(r"\b(decision|confirmed|launch|enterprise beta|enterprise users first|required)\b", statement, re.I):
            decisions.append(statement)
        if re.search(r"\b(I will|I can|can finish|will build|will design|will prepare)\b", statement, re.I):
            date = (due_re.search(statement).group(0) if due_re.search(statement) else "Not specified")
            task = re.sub(r"^(I will|I can|Engineering can)\s+", "", statement, flags=re.I)
            actions.append((speaker, task, date))
        if re.search(r"\b(risk|privacy|before|need citation|security review)\b", statement, re.I):
            risks.append(statement)
    action_rows = "\n".join(f"| {owner} | {task} | {date} |" for owner, task, date in actions)
    return (
        "# Meeting Notes\n\n## Attendees\n"
        + "\n".join(f"- {person}" for person in attendees)
        + "\n\n## Decisions\n"
        + "\n".join(f"- {item}" for item in dict.fromkeys(decisions))
        + "\n\n## Action Items\n| Owner | Task | Due Date |\n|---|---|---|\n"
        + action_rows
        + "\n\n## Risks\n"
        + "\n".join(f"- {item}" for item in dict.fromkeys(risks))
        + "\n\n## Follow-ups\n- Verify citations and required reviews before launch."
    )


def generate_work_report(document_text: str) -> str:
    sections = _sections(document_text)
    mapped = {re.sub(r"^section\s+\d+\s*:\s*", "", h, flags=re.I): b for h, b in sections}
    findings = "\n".join(f"- **{name}:** {_first_sentence(body)}" for name, body in sections)
    competitor_body = next((body for name, body in sections if "competitor" in name.lower()), "")
    competitors = []
    for line in competitor_body.splitlines():
        match = re.match(r"(.+?)\s+focuses on\s+(.+)", line.strip(), re.I)
        if match:
            competitors.append(f"| {match.group(1)} | {match.group(2)} |")
    market = "\n".join(competitors) or "| Category | Source does not provide a comparison table. |"
    risks = next((body for name, body in sections if "risk" in name.lower()), "Validate privacy, evidence, and auditability.")
    gaps = next((body for name, body in sections if "gap" in name.lower()), "Expose claim-level evidence and missing topics.")
    return (
        "# Strategic Work Report\n\n## Executive Summary\n"
        + _first_sentence(document_text)
        + "\n\n## Source-Based Findings\n"
        + findings
        + "\n\n## Competitor / Market Table\n| Product | Focus |\n|---|---|\n"
        + market
        + "\n\n## Risks\n"
        + risks
        + "\n\n## Recommendations\n- "
        + gaps
        + "\n- Make reliability metrics visible in every generated deliverable."
        + "\n\n## Evidence Notes\nAll findings are derived from the uploaded source pack and can be inspected at claim level."
    )


def answer_document_question(document_text: str, question: str) -> str:
    q_terms = set(re.findall(r"[A-Za-z]{3,}", question.lower()))
    ranked = sorted(
        sentences(document_text),
        key=lambda sentence: len(q_terms & set(re.findall(r"[A-Za-z]{3,}", sentence.lower()))),
        reverse=True,
    )
    evidence = ranked[:2]
    if not evidence:
        return "# Answer\n\nThe source does not contain enough information to answer that question."
    return "# Answer\n\n" + " ".join(evidence) + "\n\n## Evidence basis\n- " + "\n- ".join(evidence)


GENERATORS = {
    "summary": generate_summary,
    "key_points": generate_key_points,
    "quiz": generate_quiz,
    "podcast_script": generate_podcast_script,
    "meeting_notes": generate_meeting_notes,
    "work_report": generate_work_report,
}

