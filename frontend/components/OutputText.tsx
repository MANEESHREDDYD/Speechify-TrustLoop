"use client";

import { Play, Square } from "lucide-react";
import { useState } from "react";

export default function OutputText({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false);

  function toggleSpeech() {
    if (!("speechSynthesis" in window)) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text.replaceAll("#", ""));
    utterance.rate = 1.02;
    utterance.onend = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  }

  return (
    <section className="panel output-panel">
      <div className="panel-heading">
        <div><span className="eyebrow">Generated deliverable</span><h2>Generated output</h2></div>
        <button className="secondary-button small" onClick={toggleSpeech}>
          {speaking ? <Square size={15} /> : <Play size={15} />}
          {speaking ? "Stop" : "Listen"}
        </button>
      </div>
      <div className="generated-copy">
        {text.split("\n").map((line, index) => {
          if (line.startsWith("# ")) return <h2 key={index}>{line.slice(2)}</h2>;
          if (line.startsWith("## ")) return <h3 key={index}>{line.slice(3)}</h3>;
          if (line.startsWith("- ")) return <p className="bullet" key={index}>{line.slice(2)}</p>;
          if (line.startsWith("|")) return <p className="table-line" key={index}>{line}</p>;
          return line ? <p key={index}>{line}</p> : <br key={index} />;
        })}
      </div>
    </section>
  );
}
