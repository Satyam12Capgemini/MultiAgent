export interface User {
  id: string;
  email: string;
  role: 'customer' | 'agent' | 'admin';
  customer_id?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Citation {
  n: number;
  chunk_id: string;
  title: string;
}

export interface TicketMessage {
  id: string;
  ticket_id: string;
  role: 'customer' | 'assistant' | 'human_agent' | 'system';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Ticket {
  id: string;
  customer_id: string;
  subject?: string;
  category?: 'billing' | 'tech' | 'general';
  status: 'open' | 'answered' | 'escalated' | 'resolved' | 'closed';
  last_critic_score?: number;
  loops: number;
  created_at: string;
  updated_at: string;
  messages?: TicketMessage[];
}

export interface TicketEvent {
  seq: number;
  node: string;
  event_type: string;
  payload?: any;
  duration_ms?: number;
  created_at: string;
}

export interface RunTrace {
  run_id: string;
  events: TicketEvent[];
}

export interface Escalation {
  id: string;
  ticket_id: string;
  reason: string;
  summary?: string;
  context?: any;
  status: 'open' | 'claimed' | 'resolved';
  claimed_by?: string;
  created_at: string;
  resolved_at?: string;
}

export interface KBDocument {
  id: string;
  title: string;
  category: string;
  source?: string;
  file_hash: string;
  status: 'pending' | 'processing' | 'indexed' | 'failed';
  error?: string;
  chunk_count: number;
  created_at: string;
}

export interface EvalRun {
  id: string;
  dataset_id: string;
  label: string;
  critic_enabled: boolean;
  status: string;
  summary_metrics?: any;
  created_at: string;
  completed_at?: string;
}

export interface AnalyticsSummary {
  total_tickets: number;
  escalation_rate: number;
  avg_critic_score: number;
  avg_loops_per_ticket: number;
  avg_latency_ms: number;
  total_tokens_used: number;
  categories: { category: string; count: number; percentage: number }[];
  statuses: { status: string; count: number }[];
}
