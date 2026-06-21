"use client";

import Link from "next/link";
import { ArrowRight, FileSearch, LoaderCircle } from "lucide-react";
import { FormEvent, useState } from "react";
import ClaimEvidenceList from "@/components/ClaimEvidenceList";
import MissingTopicsPanel from "@/components/MissingTopicsPanel";
import PageHeader from "@/components/PageHeader";
import TrustCard from "@/components/TrustCard";
import { api } from "@/lib/api";
import { ManualAuditResult } from "@/lib/types";

const outputTypes = [
  ["summary", "Summary"],
  ["key_points", "Key points"],
  ["quiz", "Quiz"],
  ["podcast_script", "Podcast script"],
  ["meeting_notes", "Meeting notes"],
  ["work_report", "Work report"],
  ["ask_document", "Document answer"],
] as const;

export default function AuditPage() {
  const [sourceTitle, setSourceTitle] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [generatedText, setGeneratedText] = useState("");
  const [outputType, setOutputType] = useState("summary");
  const [result, setResult] = useState<ManualAuditResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!sourceTitle.trim()) {
      setError("Source title is required.");
      return;
    }
    if (!sourceText.trim()) {
      setError("Source document text is required.");
      return;
    }
    if (!generatedText.trim()) {
      setError("Generated output text is required.");
      return;
    }

    setBusy(true);
    try {
      const response = await api<ManualAuditResult>("/api/audit/manual", {
        method: "POST",
        body: JSON.stringify({
          user_id: "demo-user",
          source_title: sourceTitle,
          source_text: sourceText,
          output_type: outputType,
          generated_text: generatedText,
        }),
      });
      setResult(response);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "The backend could not complete the audit.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="External output review"
        title="Manual audit"
        description="Paste source text and an output created elsewhere. S TrustLoop stores and evaluates the pasted output without calling its deterministic generator."
      />

      <form className="audit-form panel" onSubmit={submit}>
        <div className="audit-field compact">
          <label htmlFor="source-title">Source title</label>
          <input id="source-title" value={sourceTitle} onChange={(event) => setSourceTitle(event.target.value)} placeholder="Example: Remote work security policy" />
        </div>
        <div className="audit-field compact">
          <label htmlFor="output-type">Output type</label>
          <select id="output-type" value={outputType} onChange={(event) => setOutputType(event.target.value)}>
            {outputTypes.map(([value, text]) => <option value={value} key={value}>{text}</option>)}
          </select>
        </div>
        <div className="audit-field">
          <label htmlFor="source-text">Source document text</label>
          <textarea id="source-text" value={sourceText} onChange={(event) => setSourceText(event.target.value)} placeholder="Paste the complete non-sensitive source text…" />
        </div>
        <div className="audit-field">
          <label htmlFor="generated-text">Generated output text</label>
          <textarea id="generated-text" value={generatedText} onChange={(event) => setGeneratedText(event.target.value)} placeholder="Paste an externally generated summary, note, answer, or report…" />
        </div>
        <div className="audit-submit">
          <p>This is a lexical and rule-based review signal, not proof of factual correctness.</p>
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? <LoaderCircle className="spin" size={17} /> : <FileSearch size={17} />}
            {busy ? "Evaluating…" : "Evaluate output"}
          </button>
        </div>
        {error && <div className="audit-error" role="alert">{error}</div>}
      </form>

      {result && (
        <section className="audit-results">
          <div className="section-line audit-result-title">
            <div><span className="eyebrow">Manual audit result</span><h2>External output review</h2></div>
            <Link className="secondary-button" href={`/outputs/${result.output_id}`}>Open full output page <ArrowRight size={15} /></Link>
          </div>
          <TrustCard data={result.trust_card} />
          <div className="output-layout">
            <div className="output-main"><ClaimEvidenceList claims={result.claim_checks} /></div>
            <aside className="output-side"><MissingTopicsPanel topics={result.missing_topics} /></aside>
          </div>
        </section>
      )}
    </div>
  );
}
