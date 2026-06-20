"use client";

import { useState } from "react";
import { Check, MessageSquareWarning, ThumbsDown, ThumbsUp } from "lucide-react";
import { api } from "@/lib/api";

const feedback = [
  ["correct", "Correct", Check],
  ["great_output", "Great output", ThumbsUp],
  ["missing_key_point", "Missing point", MessageSquareWarning],
  ["wrong", "Wrong", ThumbsDown],
] as const;

export default function FeedbackButtons({ outputId }: { outputId: string }) {
  const [sent, setSent] = useState<string | null>(null);
  async function submit(type: string) {
    await api("/api/feedback", {
      method: "POST",
      body: JSON.stringify({ user_id: "demo-user", output_id: outputId, feedback_type: type }),
    });
    setSent(type);
  }
  return (
    <section className="panel feedback-panel">
      <div><span className="eyebrow">Human signal</span><h2>Was this useful?</h2><p>Feedback updates quality analytics and learning memory.</p></div>
      <div className="feedback-actions">
        {feedback.map(([type, text, Icon]) => (
          <button key={type} className={sent === type ? "selected" : ""} onClick={() => submit(type)}>
            <Icon size={16} /> {sent === type ? "Saved" : text}
          </button>
        ))}
      </div>
    </section>
  );
}

