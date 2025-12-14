import axios from 'axios'
import type {
  Model,
  Task,
  Run,
  RunDetail,
  Result,
  LeaderboardEntry,
  CredentialStatus,
  CreateRunRequest,
} from './types'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Models API
export const modelsApi = {
  list: () => api.get<Model[]>('/models'),
  checkCredentials: () => api.get<CredentialStatus>('/models/credentials'),
}

// Tasks API
export const tasksApi = {
  list: () => api.get<Task[]>('/tasks'),
  get: (taskId: string) => api.get<Task>(`/tasks/${taskId}`),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/tasks/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  test: (taskId: string, modelId: string, numSamples: number = 5) =>
    api.post(`/tasks/${taskId}/test`, null, {
      params: { model_id: modelId, num_samples: numSamples },
    }),
}

// Runs API
export const runsApi = {
  list: (status?: string) =>
    api.get<Run[]>('/runs', {
      params: status ? { status } : undefined,
    }),
  get: (runId: string) => api.get<RunDetail>(`/runs/${runId}`),
  create: (data: CreateRunRequest) => api.post<Run>('/runs', data),
  getResults: (runId: string) => api.get<Result[]>(`/runs/${runId}/results`),
  getLeaderboard: (runId: string) =>
    api.get<LeaderboardEntry[]>(`/runs/${runId}/leaderboard`),
  getLogs: (runId: string) => api.get(`/runs/${runId}/logs`),
  delete: (runId: string) => api.delete(`/runs/${runId}`),
  exportCSV: (runId: string) => {
    window.open(`${API_BASE_URL}/exports/${runId}.csv`, '_blank')
  },
}

export default api
