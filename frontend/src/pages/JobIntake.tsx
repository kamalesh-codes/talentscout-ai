import { useState } from 'react'
import { startSearch, uploadResume } from '../api'
import { Badge, PrivacyNotice } from '../components/common'
import type { Filters } from '../types'

const STAGES: { key: string; label: string }[] = [
  { key: 'extracting_criteria', label: 'Extracting criteria' },
  { key: 'creating_search_strategy', label: 'Creating search strategy' },
  { key: 'searching_public_sources', label: 'Searching public sources' },
  { key: 'analyzing_projects_and_profiles', label: 'Analyzing projects and profiles' },
  { key: 'ranking_candidates', label: 'Ranking candidates' },
]

export { STAGES }

export default function JobIntake({ onStarted }: { onStarted: (runId: string) => void }) {
  const [jobDescription, setJobDescription] = useState('')
  const [filters, setFilters] = useState<Filters>({
    location: '',
    minimum_years_experience: null,
    work_mode: '',
    max_candidates: 3,
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [resumeStatus, setResumeStatus] = useState('')

  async function submit() {
    setError('')
    setBusy(true)
    try {
      const { run_id } = await startSearch(jobDescription, null, filters)
      onStarted(run_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  async function onResume(file: File | undefined) {
    if (!file) return
    setResumeStatus(`Uploading ${file.name}…`)
    try {
      const result = await uploadResume(file, { name: file.name.replace(/\.[^.]+$/, '') })
      setResumeStatus(`${result.filename}: ${result.characters_extracted} characters extracted`)
    } catch (err) {
      setResumeStatus(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-3xl font-semibold text-ink-900">Describe the role</h1>
      <p className="mt-2 text-sm text-ink-500">
        The agent extracts hiring criteria first, then searches public sources for evidence.
      </p>

      <textarea
        value={jobDescription}
        onChange={(event) => setJobDescription(event.target.value)}
        rows={14}
        placeholder="Paste the full job description…"
        className="mt-6 w-full rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed text-ink-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
      />

      <div className="mt-6 grid gap-4 sm:grid-cols-4">
        <label className="text-sm">
          <span className="text-ink-700">Location</span>
          <input
            value={filters.location}
            onChange={(event) => setFilters({ ...filters, location: event.target.value })}
            placeholder="Berlin, remote EU…"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>
        <label className="text-sm">
          <span className="text-ink-700">Min. experience (years)</span>
          <input
            type="number"
            min={0}
            value={filters.minimum_years_experience ?? ''}
            onChange={(event) =>
              setFilters({
                ...filters,
                minimum_years_experience: event.target.value === '' ? null : Number(event.target.value),
              })
            }
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>
        <label className="text-sm">
          <span className="text-ink-700">Work mode</span>
          <select
            value={filters.work_mode}
            onChange={(event) => setFilters({ ...filters, work_mode: event.target.value as Filters['work_mode'] })}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            <option value="">Any</option>
            <option value="remote">Remote</option>
            <option value="onsite">On-site</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="text-ink-700">Max candidates</span>
          <input
            type="number"
            min={1}
            max={15}
            value={filters.max_candidates}
            onChange={(event) => setFilters({ ...filters, max_candidates: Number(event.target.value) })}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        <button
          type="button"
          disabled={busy || jobDescription.trim().length < 20}
          onClick={submit}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {busy ? 'Starting…' : 'Find candidates'}
        </button>
        <label className="cursor-pointer text-sm text-indigo-600 underline underline-offset-2">
          Upload a resume
          <input
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={(event) => onResume(event.target.files?.[0])}
          />
        </label>
        {resumeStatus && <span className="text-xs text-ink-500">{resumeStatus}</span>}
      </div>
      {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}

      <div className="mt-10 rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-ink-900">Pipeline stages</h2>
        <ul className="mt-3 flex flex-wrap gap-2">
          {STAGES.map((stage) => (
            <li key={stage.key}>
              <Badge>{stage.label}</Badge>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-6">
        <PrivacyNotice />
      </div>
    </div>
  )
}
