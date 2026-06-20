import Link from "next/link";
import {
  ArrowUpRight, AudioLines, BarChart3, BookOpenCheck, Bot, CheckCircle2,
  FileCheck2, Headphones, MessageSquareText, ShieldCheck,
} from "lucide-react";
import LandingActions from "@/components/LandingActions";

const products = [
  {
    icon: BookOpenCheck,
    eyebrow: "Student learning",
    title: "From listening to measurable understanding",
    text: "Ground summaries and quizzes in the source, detect skipped concepts, and build a memory of weak topics.",
    stat: "Active recall",
  },
  {
    icon: MessageSquareText,
    eyebrow: "Meeting intelligence",
    title: "Notes that can show their work",
    text: "Verify decisions, owners, due dates, and risks against the original transcript at claim level.",
    stat: "Auditable notes",
  },
  {
    icon: Bot,
    eyebrow: "AI work reports",
    title: "A quality layer for finished deliverables",
    text: "Evaluate agent-created reports for evidence, coverage, citations, and enterprise reliability.",
    stat: "Enterprise ready",
  },
];

export default function Home() {
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><span className="pulse-dot" /> Independent local-first prototype</div>
          <h1>S <span>TrustLoop.</span></h1>
          <p><strong>AI Reliability Engine for Voice-first Learning, Meetings, and Work Agents.</strong> Ground every summary, quiz, podcast, meeting note, and AI-agent report in source evidence—then make the quality measurable.</p>
          <LandingActions />
          <div className="hero-proof">
            <span><CheckCircle2 size={14} /> No paid APIs</span>
            <span><CheckCircle2 size={14} /> Deterministic fallback</span>
            <span><CheckCircle2 size={14} /> Claim-level evidence</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="visual-glow" />
          <div className="mini-output">
            <div className="mini-top"><AudioLines size={18} /><span>Meeting notes · just now</span><i /></div>
            <h3>Beta launch is July 15.</h3>
            <div className="evidence-line"><span>Source match</span><b>96%</b></div>
            <div className="source-snippet">“Maya: Decision confirmed. Beta launch is July 15, enterprise users first.”</div>
          </div>
          <div className="floating-score">
            <span>Trust score</span><strong>92</strong><small>Highly trustworthy</small>
          </div>
          <div className="floating-risk"><ShieldCheck size={17} /><span><b>4%</b> risk</span></div>
        </div>
      </section>

      <section className="signal-strip">
        <span>OUTPUT</span><AudioLines size={18} />
        <i />
        <span>EVALUATE</span><FileCheck2 size={18} />
        <i />
        <span>EXPLAIN</span><ShieldCheck size={18} />
        <i />
        <span>IMPROVE</span><BarChart3 size={18} />
      </section>

      <section className="landing-section">
        <div className="section-intro">
          <div><span className="eyebrow">One reliability layer</span><h2>Built for where voice AI is going.</h2></div>
          <p>S TrustLoop is an independent prototype for voice-first AI reliability. It evaluates generated learning and work outputs without affiliation with or integration into any commercial platform.</p>
        </div>
        <div className="product-grid">
          {products.map(({ icon: Icon, ...item }, index) => (
            <article className="product-card" key={item.title}>
              <div className="product-number">0{index + 1}</div>
              <div className="product-icon"><Icon size={22} /></div>
              <span className="eyebrow">{item.eyebrow}</span>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
              <div className="product-footer"><span>{item.stat}</span><ArrowUpRight size={17} /></div>
            </article>
          ))}
        </div>
      </section>

      <section className="cta-band">
        <div><Headphones size={24} /><span>Ready for the 3-minute story?</span></div>
        <h2>See S TrustLoop catch a confident, wrong meeting summary.</h2>
        <Link href="/demo" className="light-button">Open guided demo <ArrowUpRight size={16} /></Link>
      </section>
    </div>
  );
}
