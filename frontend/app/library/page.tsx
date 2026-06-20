"use client";

import Link from "next/link";
import { ArrowRight, Database, FileText, Search, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import DocumentUpload from "@/components/DocumentUpload";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { api } from "@/lib/api";
import { confirmDestructiveDemoReset } from "@/lib/demoReset";
import { label } from "@/lib/format";
import { DocumentRecord } from "@/lib/types";

export default function LibraryPage() {
  const [documents, setDocuments] = useState<DocumentRecord[] | null>(null);
  const [search, setSearch] = useState("");

  async function load() {
    setDocuments(await api<DocumentRecord[]>("/api/documents"));
  }
  async function seed() {
    if (!confirmDestructiveDemoReset()) return;
    await api("/api/demo/seed", { method: "POST" });
    load();
  }
  useEffect(() => { load().catch(() => setDocuments([])); }, []);

  const filtered = documents?.filter((doc) => doc.title.toLowerCase().includes(search.toLowerCase()));
  return (
    <div className="page">
      <PageHeader
        eyebrow="Source library"
        title="Documents"
        description="The evidence base behind every generated output and trust decision."
        actions={<><button className="ghost-button" onClick={seed}><Database size={16} /> Replace with demo</button><DocumentUpload onUploaded={load} /></>}
      />
      <div className="toolbar">
        <div className="search-box"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search evidence library…" /></div>
        <span>{documents?.length || 0} sources · local SQLite</span>
      </div>
      {!documents ? <LoadingState /> : filtered?.length ? (
        <div className="library-grid">
          {filtered.map((doc) => (
            <Link className="document-card" href={`/documents/${doc.id}`} key={doc.id}>
              <div className="doc-top">
                <div className={`file-icon ${doc.source_type}`}><FileText size={19} /></div>
                <span className="source-badge">{label(doc.source_type)}</span>
              </div>
              <h3>{doc.title}</h3>
              <p>{doc.raw_text.slice(0, 120).replace(/^Title:.*\n/, "")}…</p>
              <div className="doc-stats">
                <span><b>{doc.word_count}</b> words</span>
                <span><b>{doc.chunks_count}</b> chunks</span>
                {doc.average_trust_score !== null && <span className="trust-mini"><ShieldCheck size={13} /><b>{Math.round(doc.average_trust_score)}</b></span>}
              </div>
              <div className="card-link">Open workspace <ArrowRight size={15} /></div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="empty-state"><Database size={28} /><h2>No documents yet</h2><p>Seed the synthetic demo pack or upload a local source. Demo seeding replaces all local prototype data.</p><button className="primary-button" onClick={seed}>Replace with demo data</button></div>
      )}
    </div>
  );
}
