export type Confidence = 'verified' | 'inferred' | 'unknown' | 'high' | 'medium' | 'low' | ''

export interface HiringCriteria {
  role_title: string
  seniority: string
  must_have_skills: string[]
  preferred_skills: string[]
  domain_experience: string[]
  minimum_years_experience: number | null
  location_constraints: string[]
  work_mode: string
  responsibilities: string[]
  nice_to_have: string[]
  disqualifiers: string[]
}

export interface Filters {
  location: string
  minimum_years_experience: number | null
  work_mode: '' | 'remote' | 'onsite' | 'hybrid'
  max_candidates: number
}

export interface Skill {
  name: string
  evidence: string
  source_url: string
  confidence: Confidence
}

export interface Project {
  name: string
  description: string
  technologies: string[]
  impact: string
  source_url: string
}

export interface CandidateSummary {
  id: string
  run_id: string
  name: string
  headline: string
  fit_score: number
  match_label: string
  demo_data: boolean
  top_skills: Skill[]
  projects: Project[]
  location: { value?: string; source_url?: string; confidence?: Confidence }
  profile_urls: Partial<Record<'github' | 'portfolio' | 'blog' | 'linkedin', string>>
  reasoning_summary: string
  recruiter_recommendation: string
  confidence: Confidence
  source_links: string[]
  has_resume: boolean
}

export interface Evaluation {
  fit_score?: number
  match_label?: string
  must_have_status?: { matched: string[]; missing: string[]; unknown: string[] }
  strengths?: { point: string; evidence: string; source_url: string }[]
  gaps_or_unknowns?: string[]
  reasoning_summary?: string
  recruiter_recommendation?: string
  confidence?: Confidence
}

export interface CandidateProfile {
  name?: string
  headline?: string
  location?: { value?: string; source_url?: string; confidence?: Confidence }
  profile_urls?: Partial<Record<'github' | 'portfolio' | 'blog' | 'linkedin', string>>
  skills?: Skill[]
  projects?: Project[]
  experience?: { summary?: string; years?: number | null; confidence?: Confidence }
  domain_experience?: string[]
  resume_url?: string
  source_links?: string[]
  uncertainties?: string[]
}

export interface CandidateDetail extends CandidateSummary {
  profile: CandidateProfile
  evaluation: Evaluation
  resume_filename: string
}

export interface RunProgress {
  run_id: string
  status: string
  stage: string
  message: string
  demo_data: boolean
  error: string
  criteria: Partial<HiringCriteria>
  candidate_count: number
}

export interface ProgressEvent {
  stage: string
  message: string
  status?: string
  demo_data?: boolean
  queries?: string[]
  candidate_id?: string
}
