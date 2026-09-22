import type {
  CandidateDetail,
  CandidateSummary,
  Filters,
  HiringCriteria,
  ProgressEvent,
  RunProgress,
} from './types'

export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`${response.status}: ${detail}`)
  }
  return (await response.json()) as T
}

export function analyzeJob(jobDescription: string, filters: Filters) {
  return request<{ criteria: HiringCriteria; demo_data: boolean }>('/jobs/analyze', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ job_description: jobDescription, filters }),
  })
}

export function startSearch(jobDescription: string, criteria: HiringCriteria | null, filters: Filters) {
  return request<{ run_id: string; status: string }>('/search/start', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ job_description: jobDescription, criteria, filters }),
  })
}

export function getRun(runId: string) {
  return request<RunProgress>(`/search/${runId}`)
}

export function listCandidates(runId?: string) {
  const query = runId ? `?run_id=${encodeURIComponent(runId)}` : ''
  return request<CandidateSummary[]>(`/candidates${query}`)
}

export function getCandidate(id: string) {
  return request<CandidateDetail>(`/candidates/${id}`)
}

export async function uploadResume(file: File, options: { runId?: string; candidateId?: string; name?: string }) {
  const form = new FormData()
  form.append('file', file)
  if (options.runId) form.append('run_id', options.runId)
  if (options.candidateId) form.append('candidate_id', options.candidateId)
  if (options.name) form.append('name', options.name)
  return request<{ candidate_id: string; filename: string; characters_extracted: number }>(
    '/resumes/upload',
    { method: 'POST', body: form },
  )
}

export function subscribeToRun(runId: string, onEvent: (event: ProgressEvent) => void): () => void {
  const source = new EventSource(`${API_BASE}/search/${runId}/events`)
  source.onmessage = (message) => {
    try {
      onEvent(JSON.parse(message.data) as ProgressEvent)
    } catch {
      /* ignore malformed keep-alive payloads */
    }
  }
  source.onerror = () => source.close()
  return () => source.close()
}
