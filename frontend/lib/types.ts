// lib/types.ts
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isActive: boolean;
}

export interface Transaction {
  transaction_id: string;
  date: string;
  merchant_name: string;
  amount: number;
  category: string[];
  notes: string;
  currency_symbol: string;
  currency: string;
}

export interface UploadPreviewResponse {
  preview_id: string;
  columns: string[];
  sample_rows: Record<string, unknown>[];
  suggested_mapping: Record<string, string>;
  source: string;
  schema: Record<string, unknown>;
  confidence_stats: {
    avg: number;
    min: number;
    max: number;
    count: number;
  };
}

export interface AnalysisRequest {
  query: string;
  history?: ChatMessage[];
  debug?: boolean;
}

export interface AnalysisResponse {
  response: string;
  debug?: unknown;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string | string[];
    borderColor: string | string[];
    borderWidth: number;
  }[];
}

export interface RecentActivity {
  id: string;
  userId: string;
  userName: string;
  action: string;
  target: string;
  timestamp: string;
  icon: string;
}

export type ChatRole = 'user' | 'assistant';

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface AnalyzeRequest {
  query: string;
  history?: ChatMessage[];
  debug?: boolean;
  conversation_id?: string;
  user_id?: string;
}

export interface AnalyzeResponse {
  response: string;
  conversation_id?: string;
  history?: ChatMessage[];
  debug?: unknown;
}
