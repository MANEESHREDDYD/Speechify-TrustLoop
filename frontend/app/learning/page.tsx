"use client";

import { BookOpen, BrainCircuit, RefreshCw, Sparkles, Target } from "lucide-react";
import { useEffect, useState } from "react";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { api } from "@/lib/api";

type Topic = { topic: string; strength_score: number };
type Memory = {
  user_id: string;
  strong_topics: Topic[];
  weak_topics: Topic[];
  recommended_recap: string[];
  documents_studied: number;
};

export default function LearningPage() {
  const [memory, setMemory] = useState<Memory | null>(null);

  async function load(recompute = false) {
    if (recompute) {
      setMemory(await api<Memory>("/api/learning-memory/recompute", {
        method: "POST",
        body: JSON.stringify({ user_id: "demo-user" }),
      }));
    } else {
      setMemory(await api<Memory>("/api/learning-memory/demo-user"));
    }
  }
  useEffect(() => { load(); }, []);

  return (
    <div className="page">
      <PageHeader
        eyebrow="Demo learning signals"
        title="Topics to review"
        description="A heuristic demo that groups source topics, quiz topics, coverage gaps, and feedback into inspectable review signals. It does not measure learning."
        actions={<button className="secondary-button" onClick={() => load(true)}><RefreshCw size={16} /> Recompute memory</button>}
      />
      {!memory ? <LoadingState /> : (
        <>
          <div className="learning-overview">
            <div className="learning-hero panel">
              <div className="brain-orb"><BrainCircuit size={34} /></div>
              <div><span className="eyebrow">Local demo profile</span><h2>{memory.documents_studied} documents indexed</h2><p>Rule-based signals from source topics, generated quizzes, missing concepts, and explicit feedback.</p></div>
            </div>
            <div className="memory-stat panel"><Target size={21} /><strong>{memory.strong_topics.length}</strong><span>strong topics</span></div>
            <div className="memory-stat panel"><BookOpen size={21} /><strong>{memory.weak_topics.length}</strong><span>review targets</span></div>
          </div>

          <div className="learning-grid">
            <section className="panel topic-strength-panel">
              <div className="panel-heading"><div><span className="eyebrow">Higher demo signal</span><h2>Stronger topic signals</h2></div></div>
              <div className="strength-list">
                {memory.strong_topics.map((topic) => (
                  <div key={topic.topic}>
                    <div><b>{topic.topic}</b><span>{Math.round(topic.strength_score * 100)}%</span></div>
                    <div className="strength-bar"><i style={{ width: `${topic.strength_score * 100}%` }} /></div>
                  </div>
                ))}
                {!memory.strong_topics.length && <p className="empty-compact">Generate a quiz to strengthen topic signals.</p>}
              </div>
            </section>
            <section className="panel topic-strength-panel weak">
              <div className="panel-heading"><div><span className="eyebrow">Lower demo signal</span><h2>Review targets</h2></div></div>
              <div className="strength-list">
                {memory.weak_topics.map((topic) => (
                  <div key={topic.topic}>
                    <div><b>{topic.topic}</b><span>{Math.round(topic.strength_score * 100)}%</span></div>
                    <div className="strength-bar"><i style={{ width: `${topic.strength_score * 100}%` }} /></div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section className="recap-panel panel">
            <div><span className="eyebrow">Next best action</span><h2>Recommended recaps</h2></div>
            <div className="recap-grid">
              {memory.recommended_recap.map((recap, index) => (
                <article key={recap}><span><Sparkles size={16} /></span><div><small>Recap {index + 1}</small><p>{recap}</p></div></article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
