import { AlertOctagon, Check, ChevronRight, Minus } from "lucide-react";
import { Claim } from "@/lib/types";

const icons = {
  supported: Check,
  weakly_supported: Minus,
  unsupported: AlertOctagon,
  contradicted: AlertOctagon,
};

export default function ClaimEvidenceList({ claims }: { claims: Claim[] }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div><span className="eyebrow">Evidence map</span><h2>Claim-level grounding</h2></div>
        <span className="count-pill">{claims.length} claims</span>
      </div>
      <div className="claim-list">
        {claims.map((claim, index) => {
          const Icon = icons[claim.status];
          return (
            <details key={claim.id} className={`claim-item ${claim.status}`} open={index < 2}>
              <summary>
                <span className="claim-icon"><Icon size={15} /></span>
                <span className="claim-copy">{claim.claim_text}</span>
                <span className="confidence">{Math.round(claim.confidence * 100)}%</span>
                <ChevronRight className="chevron" size={16} />
              </summary>
              <div className="evidence">
                <div className="evidence-meta">
                  <span>{claim.section_title || "No direct section"}</span>
                  {claim.page_number && <span>Page {claim.page_number}</span>}
                </div>
                <p>{claim.supporting_text || "No sufficiently similar source evidence was found."}</p>
              </div>
            </details>
          );
        })}
      </div>
    </section>
  );
}

