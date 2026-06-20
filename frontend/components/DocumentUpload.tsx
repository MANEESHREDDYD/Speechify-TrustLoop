"use client";

import { ChangeEvent, useRef, useState } from "react";
import { FileUp, LoaderCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function DocumentUpload({ onUploaded }: { onUploaded: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    const form = new FormData();
    form.append("file", file);
    await api("/api/documents/upload", { method: "POST", body: form });
    setBusy(false);
    onUploaded();
  }
  return (
    <>
      <input hidden ref={inputRef} type="file" accept=".txt,.md,.pdf,.docx" onChange={upload} />
      <button className="secondary-button" onClick={() => inputRef.current?.click()} disabled={busy}>
        {busy ? <LoaderCircle className="spin" size={16} /> : <FileUp size={16} />}
        {busy ? "Processing…" : "Upload document"}
      </button>
    </>
  );
}

