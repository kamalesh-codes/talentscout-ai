import { useEffect, useMemo, useState } from 'react'
import { listCandidates } from '../api'
import CandidateCard from '../components/CandidateCard'
import CandidatePanel from '../components/CandidatePanel'
import { Badge, PrivacyNotice } from '../components/common'
import type { CandidateSummary } from '../types'

type SourceFilter = 'all' | 'github' | 'portfolio' | 'blog' | 'linkedin' | 'resume'

export default function Dashboard({ runId, onNewSearch }: { runId?: string; onNewSearch: () => void }) {
  const [candidates, setCandidates] = useState<CandidateSummary[]>([])
  const [minScore, setMinScore] = useState(0)
  const [skillQuery, setSkillQuery] = useState('')
  const [source, setSource] = useState<SourceFilter>('all')
  const [verifiedOnly, setVerifiedOnly] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const [error, setError] = useState('')

  async function refresh() {
    try {
      setCandidates(await listCandidates(runId))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId])

  const visible = useMemo(() => {
    const skills = skillQuery
      .split(',')
      .map((value) => value.trim().toLowerCase())
      .filter(Boolean)
    return candidates.filter((candidate) => {
      if (candidate.fit_score < minScore) return false
      if (source === 'resume' && !candidate.has_resume) return false
      if (source !== 'all' && source !== 'resume' && !candidate.profile_urls[source]) return false
      if (verifiedOnly && candidate.location?.confidence !== 'verified') return false
      if (skills.length > 0) {
        const owned = candidate.top_skills.map((skill) => skill.name.toLowerCase())
        if (!skills.every((skill) => owned.some((name) => name.includes(skill)))) return false
      }
      return true
    })
  }, [candidates, minScore, skillQuery, source, verifiedOnly])

  const demo = candidates.some((candidate) => candidate.demo_data)

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-ink-900">Ranked candidates</h1>
          <p className="mt-1 text-sm text-ink-500">
            {visible.length} of {candidates.length} shown · scores are recommendations, not hiring decisions
          </p>
        </div>
        <div className="flex items-center gap-3">
          {demo && <Badge tone="amber">Demo data</Badge>}
          <button
            type="button"
            onClick={onNewSearch}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            New search
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-4">
        <label className="text-sm">
          <span className="text-ink-700">Minimum score: {minScore}</span>
          <input
            type="range"
            min={0}
            max={100}
            value={minScore}
            onChange={(event) => setMinScore(Number(event.target.value))}
            className="mt-2 w-full accent-indigo-600"
          />
        </label>
        <label className="text-sm">
          <span className="text-ink-700">Required skills</span>
          <input
            value={skillQuery}
            onChange={(event) => setSkillQuery(event.target.value)}
            placeholder="python, fastapi"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>
        <label className="text-sm">
          <span className="text-ink-700">Source type</span>
          <select
            value={source}
            onChange={(event) => setSource(event.target.value as SourceFilter)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            <option value="all">All sources</option>
            <option value="github">GitHub</option>
            <option value="portfolio">Portfolio</option>
            <option value="blog">Blog</option>
            <option value="linkedin">LinkedIn</option>
            <option value="resume">Resume</option>
          </select>
        </label>
        <label className="flex items-end gap-2 text-sm text-ink-700">
          <input
            type="checkbox"
            checked={verifiedOnly}
            onChange={(event) => setVerifiedOnly(event.target.checked)}
            className="h-4 w-4 accent-indigo-600"
          />
          Verified location only
        </label>
      </div>

      {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}

      <div className="mt-6 space-y-4">
        {visible.map((candidate) => (
          <CandidateCard key={candidate.id} candidate={candidate} onOpen={() => setSelected(candidate.id)} />
        ))}
        {visible.length === 0 && (
          <p className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-ink-500">
            No candidates match the current filters.
          </p>
        )}
      </div>

      <div className="mt-8">
        <PrivacyNotice />
      </div>

      {selected && (
        <CandidatePanel candidateId={selected} onClose={() => setSelected(null)} onChanged={refresh} />
      )}
    </div>
  )
}
