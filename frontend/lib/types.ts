export type TrustCardData = {
  evaluation_id: string;
  output_id: string;
  trust_score: number;
  label: string;
  grounding_score: number;
  coverage_score: number;
  citation_score: number;
  readability_score: number;
  hallucination_risk: number;
  supported_claims: number;
  weakly_supported_claims: number;
  unsupported_claims: number;
  contradicted_claims: number;
  missing_topics_count: number;
};

export type DocumentRecord = {
  id: string;
  title: string;
  source_type: string;
  file_type: string;
  raw_text: string;
  word_count: number;
  page_count: number;
  processing_status: string;
  chunks_count: number;
  average_trust_score: number | null;
};

export type OutputRecord = {
  id: string;
  output_id: string;
  document_id: string;
  output_type: string;
  prompt: string;
  generated_text: string;
  generation_mode: string;
  created_at: string;
  trust_card: TrustCardData | null;
};

export type Claim = {
  id: string;
  claim_text: string;
  status: "supported" | "weakly_supported" | "unsupported" | "contradicted";
  confidence: number;
  supporting_text: string;
  section_title?: string;
  page_number?: number;
};

export type MissingTopic = {
  id: string;
  topic: string;
  importance_score: number;
  reason: string;
};

