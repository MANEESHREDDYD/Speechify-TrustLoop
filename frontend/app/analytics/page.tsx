"use client";

import { BarChart3, Database, FileCheck2, Gauge, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { api } from "@/lib/api";
import { label } from "@/lib/format";

type Overview = {
  documents_count: number;
  outputs_count: number;
  evaluations_count: number;
  average_trust_score: number;
  average_hallucination_risk: number;
  most_common_missing_topics: string[];
  feedback_distribution: Record<string, number>;
};
type ByType = {
  output_type: string;
  average_trust_score: number;
  average_hallucination_risk: number;
  evaluations: number;
};
type TopicCount = { topic: string; count: number };

const COLORS = ["#8b5cf6", "#31d0aa", "#ffbd59", "#ff6b7a", "#60a5fa"];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [byType, setByType] = useState<ByType[]>([]);
  const [topics, setTopics] = useState<TopicCount[]>([]);

  async function load() {
    const [summary, types, missing] = await Promise.all([
      api<Overview>("/api/analytics/overview"),
      api<ByType[]>("/api/analytics/trust-by-output-type"),
      api<TopicCount[]>("/api/analytics/missing-topics"),
    ]);
    setOverview(summary); setByType(types.map((item) => ({ ...item, output_type: label(item.output_type) }))); setTopics(missing);
  }
  async function seed() { await api("/api/demo/seed", { method: "POST" }); load(); }
  useEffect(() => { load(); }, []);

  const feedbackData = Object.entries(overview?.feedback_distribution || {}).map(([name, value]) => ({ name: label(name), value }));
  return (
    <div className="page">
      <PageHeader
        eyebrow="Quality operations"
        title="Reliability analytics"
        description="A portfolio view of grounding, risk, coverage gaps, and human feedback across AI-generated work."
        actions={<button className="secondary-button" onClick={seed}><Database size={16} /> Refresh demo data</button>}
      />
      {!overview ? <LoadingState /> : (
        <>
          <div className="stat-grid">
            <article className="stat-card"><Database size={19} /><span>Documents</span><strong>{overview.documents_count}</strong><small>source packs indexed</small></article>
            <article className="stat-card"><FileCheck2 size={19} /><span>Evaluations</span><strong>{overview.evaluations_count}</strong><small>{overview.outputs_count} AI outputs</small></article>
            <article className="stat-card accent"><Gauge size={19} /><span>Average trust</span><strong>{overview.average_trust_score}</strong><small>across all output types</small></article>
            <article className="stat-card risk"><ShieldAlert size={19} /><span>Hallucination risk</span><strong>{Math.round(overview.average_hallucination_risk * 100)}%</strong><small>portfolio average</small></article>
          </div>

          <div className="analytics-grid">
            <section className="panel chart-panel wide">
              <div className="panel-heading"><div><span className="eyebrow">Model quality</span><h2>Trust by output type</h2></div><BarChart3 size={19} /></div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={byType} margin={{ top: 8, right: 10, left: -20, bottom: 10 }}>
                    <CartesianGrid stroke="#252634" vertical={false} />
                    <XAxis dataKey="output_type" tick={{ fill: "#8f91a3", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fill: "#77798a", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{ fill: "#ffffff08" }} contentStyle={{ background: "#171820", border: "1px solid #30313f", borderRadius: 10 }} />
                    <Bar dataKey="average_trust_score" name="Trust score" radius={[7, 7, 0, 0]}>
                      {byType.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="panel chart-panel">
              <div className="panel-heading"><div><span className="eyebrow">Human feedback</span><h2>Feedback signals</h2></div></div>
              {feedbackData.length ? <div className="chart-box donut">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart><Pie data={feedbackData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={82} paddingAngle={4}>
                    {feedbackData.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                  </Pie><Tooltip contentStyle={{ background: "#171820", border: "1px solid #30313f", borderRadius: 10 }} /></PieChart>
                </ResponsiveContainer>
              </div> : <div className="chart-empty">Feedback appears here after reviewers rate an output.</div>}
            </section>

            <section className="panel chart-panel">
              <div className="panel-heading"><div><span className="eyebrow">Coverage intelligence</span><h2>Common missing topics</h2></div></div>
              <div className="rank-list">
                {topics.slice(0, 6).map((topic, index) => (
                  <div key={topic.topic}><span>0{index + 1}</span><b>{topic.topic}</b><i>{topic.count}×</i></div>
                ))}
              </div>
            </section>
          </div>
        </>
      )}
    </div>
  );
}

