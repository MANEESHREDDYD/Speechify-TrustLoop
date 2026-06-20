"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, AudioLines, Bot, FileQuestion, FileText, HelpCircle,
  ListChecks, LoaderCircle, MessageSquareText, Send, Sparkles,
} from "lucide-react";
import { useEffect, useState } from "react";
import LoadingState from "@/components/LoadingState";
import { api, generateAndEvaluate } from "@/lib/api";
import { label } from "@/lib/format";
import { DocumentRecord, OutputRecord } from "@/lib/types";

type Chunk = { id: string; chunk_index: number; section_title: string; page_number: number; text: string };

const generators = [
  ["summary", "Summary", Sparkles],
  ["key_points", "Key points", ListChecks],
  ["quiz", "Quiz", HelpCircle],
  ["podcast_script", "Podcast", AudioLines],
  ["meeting_notes", "Meeting notes", MessageSquareText],
  ["work_report", "Work report", Bot],
] as const;

export default function DocumentPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [document, setDocument] = useState<DocumentRecord | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [outputs, setOutputs] = useState<OutputRecord[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [question, setQuestion] = useState("");

  useEffect(() => {
    Promise.all([
      api<DocumentRecord>(`/api/documents/${id}`),
      api<Chunk[]>(`/api/documents/${id}/chunks`),
      api<OutputRecord[]>(`/api/outputs?document_id=${id}`),
    ]).then(([doc, chunkList, outputList]) => {
      setDocument(doc); setChunks(chunkList); setOutputs(outputList);
    });
  }, [id]);

  async function generate(type: string) {
    setBusy(type);
    const outputId = await generateAndEvaluate(id, type);
    router.push(`/outputs/${outputId}`);
  }
  async function ask() {
    if (!question.trim()) return;
    setBusy("ask");
    const output = await api<{ output_id: string }>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ document_id: id, user_id: "demo-user", prompt: question }),
    });
    await api(`/api/evaluate/${output.output_id}`, { method: "POST" });
    router.push(`/outputs/${output.output_id}`);
  }

  if (!document) return <div className="page"><LoadingState label="Opening source workspace…" /></div>;
  return (
    <div className="page">
      <Link href="/library" className="back-link"><ArrowLeft size={15} /> Back to library</Link>
      <header className="workspace-header">
        <div>
          <div className="eyebrow">{label(document.source_type)} source · {document.file_type.toUpperCase()}</div>
          <h1>{document.title}</h1>
          <p>{document.word_count} words · {chunks.length} evidence chunks · ready for local generation</p>
        </div>
        <span className="ready-pill"><span /> Source processed</span>
      </header>

      <div className="workspace-grid">
        <section className="panel document-preview">
          <div className="panel-heading">
            <div><span className="eyebrow">Source of truth</span><h2>Document preview</h2></div>
            <FileText size={19} />
          </div>
          <div className="source-copy">{document.raw_text}</div>
        </section>

        <aside className="workspace-actions">
          <section className="panel generate-panel">
            <span className="eyebrow">Create + evaluate</span>
            <h2>Generate an output</h2>
            <p>Every output is saved, evaluated, and linked back to source evidence.</p>
            <div className="generate-grid">
              {generators.map(([type, text, Icon]) => (
                <button onClick={() => generate(type)} disabled={!!busy} key={type}>
                  {busy === type ? <LoaderCircle className="spin" size={18} /> : <Icon size={18} />}
                  <span>{text}</span>
                </button>
              ))}
            </div>
          </section>
          <section className="panel ask-panel">
            <div className="ask-title"><FileQuestion size={18} /><b>Ask this document</b></div>
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What are the biggest risks?" />
            <button className="primary-button" onClick={ask} disabled={!!busy || !question.trim()}>
              {busy === "ask" ? <LoaderCircle className="spin" size={16} /> : <Send size={16} />} Ask + verify
            </button>
          </section>
        </aside>
      </div>

      <section className="panel chunk-panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Retrieval index</span><h2>Evidence chunks</h2></div>
          <span className="count-pill">{chunks.length} local chunks</span>
        </div>
        <div className="chunk-grid">
          {chunks.map((chunk) => (
            <article key={chunk.id}>
              <span>#{chunk.chunk_index + 1} · {chunk.section_title}</span>
              <p>{chunk.text}</p>
            </article>
          ))}
        </div>
      </section>

      {!!outputs.length && (
        <section className="recent-section">
          <div className="section-line"><div><span className="eyebrow">History</span><h2>Recent outputs</h2></div></div>
          <div className="output-card-grid">
            {outputs.slice(0, 6).map((output) => (
              <Link href={`/outputs/${output.id}`} className="output-card" key={output.id}>
                <span>{label(output.output_type)}</span>
                <h3>{output.generated_text.split("\n").find((line) => !line.startsWith("#") && line.length > 10)?.slice(0, 80) || "Generated output"}</h3>
                <div>
                  <small>{label(output.generation_mode)}</small>
                  {output.trust_card && <b>{Math.round(output.trust_card.trust_score)} trust</b>}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

