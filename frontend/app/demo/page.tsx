"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertTriangle, ArrowRight, BookOpenCheck, Bot, CheckCircle2, Database,
  LoaderCircle, MessageSquareText, Play, ShieldCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { api, generateAndEvaluate } from "@/lib/api";
import { DocumentRecord, OutputRecord } from "@/lib/types";

const flows = [
  {
    key: "student",
    icon: BookOpenCheck,
    number: "01",
    title: "Student learning",
    message: "Turn passive listening into measurable learning.",
    documentTitle: "Voice AI and Accessible Learning",
    outputType: "summary",
    button: "Generate grounded summary",
    tint: "violet",
  },
  {
    key: "meeting",
    icon: MessageSquareText,
    number: "02",
    title: "Meeting notes",
    message: "Make every decision, owner, and date auditable.",
    documentTitle: "Voice AI Meeting Notes Product Launch",
    outputType: "meeting_notes",
    button: "Generate auditable notes",
    tint: "green",
  },
  {
    key: "work",
    icon: Bot,
    number: "03",
    title: "Speechify Work",
    message: "Add a quality layer behind finished agent work.",
    documentTitle: "Voice-first Productivity Market Analysis",
    outputType: "work_report",
    button: "Generate work report",
    tint: "blue",
  },
] as const;

export default function DemoPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentRecord[] | null>(null);
  const [outputs, setOutputs] = useState<OutputRecord[]>([]);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    let docs = await api<DocumentRecord[]>("/api/documents");
    if (!docs.length) {
      await api("/api/demo/seed", { method: "POST" });
      docs = await api<DocumentRecord[]>("/api/documents");
    }
    setDocuments(docs);
    setOutputs(await api<OutputRecord[]>("/api/outputs"));
  }
  useEffect(() => { load(); }, []);

  async function runFlow(key: string, documentTitle: string, outputType: string) {
    const document = documents?.find((item) => item.title === documentTitle);
    if (!document) return;
    setBusy(key);
    const outputId = await generateAndEvaluate(document.id, outputType);
    router.push(`/outputs/${outputId}`);
  }
  async function reset() {
    setBusy("reset");
    await api("/api/demo/seed", { method: "POST" });
    await load();
    setBusy(null);
  }

  const wrongMeeting = outputs.find((output) => output.generation_mode === "negative_test" && output.output_type === "meeting_notes");
  return (
    <div className="page">
      <PageHeader
        eyebrow="3-minute product story"
        title="Guided TrustLoop demo"
        description="Three one-click flows showing how reliability changes learning, meetings, and AI-generated work."
        actions={<button className="secondary-button" onClick={reset} disabled={!!busy}><Database size={16} /> Reset clean demo</button>}
      />
      {!documents ? <LoadingState label="Preparing the synthetic demo pack…" /> : (
        <>
          <div className="demo-progress">
            <span className="active">Source</span><i /><span className="active">Generate</span><i /><span className="active">Evaluate</span><i /><span>Improve</span>
          </div>
          <div className="demo-flow-grid">
            {flows.map(({ icon: Icon, ...flow }) => {
              const document = documents.find((item) => item.title === flow.documentTitle);
              return (
                <article className={`demo-flow ${flow.tint}`} key={flow.key}>
                  <div className="demo-number">{flow.number}</div>
                  <div className="demo-icon"><Icon size={23} /></div>
                  <span className="eyebrow">{flow.title}</span>
                  <h2>{flow.message}</h2>
                  <div className="demo-source">
                    <small>Demo source</small><b>{flow.documentTitle}</b>
                    <span>{document?.word_count || 0} words · {document?.chunks_count || 0} chunks</span>
                  </div>
                  <div className="demo-checks">
                    <span><CheckCircle2 size={14} /> source grounding</span>
                    <span><CheckCircle2 size={14} /> missing topics</span>
                    <span><CheckCircle2 size={14} /> claim evidence</span>
                  </div>
                  <button className="demo-button" onClick={() => runFlow(flow.key, flow.documentTitle, flow.outputType)} disabled={!!busy}>
                    {busy === flow.key ? <LoaderCircle className="spin" size={17} /> : <Play size={17} />}
                    {busy === flow.key ? "Generating + evaluating…" : flow.button}
                  </button>
                  {document && <Link href={`/documents/${document.id}`}>Inspect source <ArrowRight size={14} /></Link>}
                </article>
              );
            })}
          </div>

          <section className="negative-demo">
            <div className="negative-icon"><AlertTriangle size={23} /></div>
            <div>
              <span className="eyebrow">The proof moment</span>
              <h2>Can TrustLoop catch confident, wrong notes?</h2>
              <p>The seeded negative test changes the launch date, assigns work to the wrong people, and removes a required privacy review.</p>
            </div>
            <div className="negative-tags"><span>Wrong date</span><span>Wrong owners</span><span>Contradicted requirement</span></div>
            {wrongMeeting ? (
              <Link className="danger-button" href={`/outputs/${wrongMeeting.id}`}><ShieldCheck size={16} /> View failed trust check</Link>
            ) : <button className="danger-button" onClick={reset}>Seed negative test</button>}
          </section>
        </>
      )}
    </div>
  );
}

