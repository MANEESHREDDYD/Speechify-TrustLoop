import { AlertTriangle, CheckCircle2, CircleDashed, Link2 } from "lucide-react";
import { percent, scoreTone } from "@/lib/format";
import { TrustCardData } from "@/lib/types";

export default function TrustCard({ data }: { data: TrustCardData }) {
  const tone = scoreTone(data.trust_score);
  const metrics = [
    ["Source overlap", data.grounding_score],
    ["Coverage", data.coverage_score],
    ["Evidence availability", data.citation_score],
    ["Readability", data.readability_score],
  ] as const;
  return (
    <section className="trust-card panel">
      <div className={`score-orb ${tone}`}>
        <div><strong>{Math.round(data.trust_score)}</strong><span>/ 100</span></div>
      </div>
      <div className="trust-summary">
        <span className={`status-label ${tone}`}>{data.label}</span>
        <h2>Heuristic review score</h2>
        <p>Transparent lexical and rule-based review signal for this output.</p>
        <div className="metric-bars">
          {metrics.map(([name, value]) => (
            <div className="metric-row" key={name}>
              <span>{name}</span><b>{percent(value)}</b>
              <div><i style={{ width: percent(value) }} /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="claim-totals">
        <div><CheckCircle2 size={17} /><span><b>{data.supported_claims}</b> supported</span></div>
        <div><CircleDashed size={17} /><span><b>{data.weakly_supported_claims}</b> weak</span></div>
        <div><AlertTriangle size={17} /><span><b>{data.unsupported_claims + data.contradicted_claims}</b> flagged</span></div>
        <div><Link2 size={17} /><span><b>{percent(data.hallucination_risk)}</b> flagged-claim risk</span></div>
      </div>
    </section>
  );
}
