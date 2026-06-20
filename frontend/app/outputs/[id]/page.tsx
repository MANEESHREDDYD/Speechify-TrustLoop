"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Calendar, Cpu } from "lucide-react";
import { useEffect, useState } from "react";
import ClaimEvidenceList from "@/components/ClaimEvidenceList";
import FeedbackButtons from "@/components/FeedbackButtons";
import LoadingState from "@/components/LoadingState";
import MissingTopicsPanel from "@/components/MissingTopicsPanel";
import OutputText from "@/components/OutputText";
import TrustCard from "@/components/TrustCard";
import { api } from "@/lib/api";
import { label } from "@/lib/format";
import { Claim, MissingTopic, OutputRecord, TrustCardData } from "@/lib/types";

export default function OutputPage() {
  const { id } = useParams<{ id: string }>();
  const [output, setOutput] = useState<OutputRecord | null>(null);
  const [card, setCard] = useState<TrustCardData | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [topics, setTopics] = useState<MissingTopic[]>([]);

  useEffect(() => {
    async function load() {
      const out = await api<OutputRecord>(`/api/outputs/${id}`);
      setOutput(out);
      let trust = out.trust_card;
      if (!trust) trust = await api<TrustCardData>(`/api/evaluate/${id}`, { method: "POST" });
      setCard(trust);
      const [claimRows, topicRows] = await Promise.all([
        api<Claim[]>(`/api/outputs/${id}/claims`),
        api<MissingTopic[]>(`/api/outputs/${id}/missing-topics`),
      ]);
      setClaims(claimRows); setTopics(topicRows);
    }
    load();
  }, [id]);

  if (!output || !card) return <div className="page"><LoadingState label="Tracing claims back to evidence…" /></div>;
  return (
    <div className="page">
      <Link href={`/documents/${output.document_id}`} className="back-link"><ArrowLeft size={15} /> Back to source</Link>
      <header className="output-header">
        <div>
          <div className="eyebrow">Evaluated output</div>
          <h1>{label(output.output_type)}</h1>
          <p><Cpu size={14} /> {label(output.generation_mode)} <span>·</span> <Calendar size={14} /> {new Date(output.created_at).toLocaleDateString()}</p>
        </div>
        <span className={`output-status ${card.hallucination_risk > .35 ? "risk" : "safe"}`}>
          {card.hallucination_risk > .35 ? "Human review recommended" : "Evidence check complete"}
        </span>
      </header>

      <TrustCard data={card} />
      <div className="output-layout">
        <div className="output-main"><OutputText text={output.generated_text} /><ClaimEvidenceList claims={claims} /></div>
        <aside className="output-side"><MissingTopicsPanel topics={topics} /><FeedbackButtons outputId={output.id} /></aside>
      </div>
    </div>
  );
}

