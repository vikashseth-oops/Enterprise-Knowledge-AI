export interface Citation {
  citation_id: number;
  doc_id: string;
  doc_name: string;
  chunk_id: string;
  page_number?: number | null;
  snippet: string;
  score: number;
  source?: string | null;
}

export interface TraceSpan {
  node: string;
  start_time_ms: number;
  duration_ms: number;
  status: string;
  metadata?: Record<string, any>;
}

export interface LatencyBreakdown {
  route_ms: number;
  rewrite_ms: number;
  retrieve_ms: number;
  grade_ms: number;
  generate_ms: number;
  verify_ms: number;
  total_ms: number;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  citations?: Citation[];
  latency?: LatencyBreakdown;
  tokens?: TokenUsage;
  trace?: TraceSpan[];
  route?: string;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  messages: ChatMessage[];
}

export interface DocumentMetadata {
  doc_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  created_at: string;
  chunk_count: number;
  status: "queued" | "processing" | "indexed" | "failed";
  error_message?: string | null;
  collection: string;
  tags: string[];
}

export interface DocumentChunk {
  chunk_id: string;
  doc_id: string;
  doc_name: string;
  chunk_index: number;
  text: string;
  page_number?: number | null;
  section?: string | null;
  token_count?: number | null;
  metadata?: Record<string, any>;
}

export interface RetrievalMetrics {
  recall_at_1: number;
  recall_at_3: number;
  recall_at_5: number;
  recall_at_10: number;
  mrr: number;
  ndcg_at_5: number;
  hit_rate: number;
  total_queries: number;
}

export interface LatencyPercentiles {
  p50_ms: number;
  p90_ms: number;
  p95_ms: number;
  p99_ms: number;
  min_ms: number;
  max_ms: number;
  avg_ms: number;
}

export interface BenchmarkReport {
  retrieval_latency: LatencyPercentiles;
  e2e_latency: LatencyPercentiles;
  concurrency_rps: number;
  concurrent_users: number;
}

export interface EvalReport {
  timestamp: string;
  dataset_size: number;
  retrieval: RetrievalMetrics;
  benchmark: BenchmarkReport;
  target_met: boolean;
  details: Record<string, any>;
}
