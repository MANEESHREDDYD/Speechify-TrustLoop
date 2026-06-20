import { ScanSearch } from "lucide-react";
import { MissingTopic } from "@/lib/types";

export default function MissingTopicsPanel({ topics }: { topics: MissingTopic[] }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div><span className="eyebrow">Coverage gaps</span><h2>Missing topics</h2></div>
        <ScanSearch size={20} />
      </div>
      {topics.length ? (
        <div className="topic-list">
          {topics.map((topic) => (
            <div key={topic.id}>
              <div><b>{topic.topic}</b><span>{Math.round(topic.importance_score * 100)}% importance</span></div>
              <p>{topic.reason}</p>
            </div>
          ))}
        </div>
      ) : <div className="empty-compact">No important source topics appear to be missing.</div>}
    </section>
  );
}

