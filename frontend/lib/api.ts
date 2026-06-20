const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options?.headers,
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const outputPath: Record<string, string> = {
  summary: "summary",
  key_points: "key-points",
  quiz: "quiz",
  podcast_script: "podcast-script",
  meeting_notes: "meeting-notes",
  work_report: "work-report",
};

export async function generateAndEvaluate(documentId: string, outputType: string) {
  const output = await api<{ output_id: string }>(`/api/generate/${outputPath[outputType]}`, {
    method: "POST",
    body: JSON.stringify({ document_id: documentId, user_id: "demo-user", mode: "deterministic" }),
  });
  await api(`/api/evaluate/${output.output_id}`, { method: "POST" });
  return output.output_id;
}

