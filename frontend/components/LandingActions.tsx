"use client";

import Link from "next/link";
import { ArrowRight, Database, LoaderCircle } from "lucide-react";
import { useState } from "react";
import { api } from "@/lib/api";

export default function LandingActions() {
  const [state, setState] = useState<"idle" | "loading" | "done">("idle");
  async function seed() {
    setState("loading");
    await api("/api/demo/seed", { method: "POST" });
    setState("done");
  }
  return (
    <div className="hero-actions">
      <button className="primary-button" onClick={seed} disabled={state === "loading"}>
        {state === "loading" ? <LoaderCircle className="spin" size={17} /> : <Database size={17} />}
        {state === "done" ? "Demo ready" : state === "loading" ? "Seeding…" : "Seed demo data"}
      </button>
      <Link className="secondary-button" href="/demo">Run guided demo <ArrowRight size={16} /></Link>
    </div>
  );
}

