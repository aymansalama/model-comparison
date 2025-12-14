export interface Model {
  id: number
  model_id: string
  provider: string
  name: string
  description: string
  is_active: boolean
  max_tokens: number
  supports_json_mode: boolean
}

export interface Task {
  id: number
  task_id: string
  name: string
  description: string
  task_type: string
  is_builtin: boolean
  is_active: boolean
  input_fields: string[]
  label_field: string
  metrics: string[]
  created_at: string
}

export interface RunConfig {
  temperature: number
  max_tokens: number
  top_p: number
  timeout: number
  max_retries: number
  sample_cap: number | null
  trials: number
  split: string
}

export interface Run {
  id: number
  run_id: string
  name: string
  description: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  config: RunConfig
  selected_models: string[]
  selected_tasks: string[]
  progress_percent: number
  created_at: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

export interface RunDetail extends Run {
  total_evaluations: number
  completed_evaluations: number
  failed_evaluations: number
  results_path: string | null
}

export interface Result {
  id: number
  task_id: string
  model_id: string
  metrics: Record<string, number>
  avg_latency_ms: number
  p50_latency_ms: number
  p95_latency_ms: number
  p99_latency_ms: number
  total_input_tokens: number
  total_output_tokens: number
  estimated_cost_usd: number
  num_samples: number
  num_errors: number
}

export interface LeaderboardEntry {
  model_id: string
  task_id: string
  metrics: Record<string, number>
  avg_latency_ms: number
  estimated_cost_usd: number
}

export interface CredentialStatus {
  openai_configured: boolean
  aws_configured: boolean
  openai_valid: boolean | null
  aws_valid: boolean | null
}

export interface CreateRunRequest {
  name?: string
  description?: string
  model_ids: string[]
  task_ids: string[]
  config?: Partial<RunConfig>
}
