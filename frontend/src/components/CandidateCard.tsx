import { Badge, DemoTag, ScoreDial } from './common'
import type { CandidateSummary } from '../types'

const SOURCE_LABELS: Record<string, string> = {
  github: 'GitHub',
  portfolio: 'Portfolio',
  blog: 'Blog',
  linkedin: 'LinkedIn',
}

export default function CandidateCard({
  candidate,
  onOpen,
}: {
  candidate: CandidateSummary
  onOpen: () => void
}) {
  const label = candidate.match_label || 'Unscored'
  const tone = label.startsWith('Strong') ? 'emerald' : label.startsWith('Potential') ? 'indigo' : 'slate'
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-semibold text-ink-900">{candidate.name}</h3>
            <Badge tone={tone}>{label}</Badge>
            {candidate.demo_data && <DemoTag />}
          </div>
          <p className="mt-1 text-sm text-ink-700">{candidate.headline}</p>
          {candidate.location?.value && (
            <p className="mt-1 text-xs text-ink-500">
              {candidate.location.value} · {candidate.location.confidence}
            </p>
          )}
        </div>
        <ScoreDial score={candidate.fit_score} />
      </div>

      {candidate.top_skills.length > 0 && (
        <ul className="mt-4 flex flex-wrap gap-2">
          {candidate.top_skills.map((skill, index) => (
            <li key={`${skill.name}-${index}`}>
              <Badge tone="indigo">{skill.name}</Badge>
            </li>
          ))}
        </ul>
      )}

      {candidate.projects.length > 0 && (
        <p className="mt-3 text-sm text-ink-700">
          <span className="font-medium">Relevant work:</span>{' '}
          {candidate.projects.map((project) => project.name).filter(Boolean).join(', ')}
        </p>
      )}

      {candidate.reasoning_summary && (
        <div className="mt-4 rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">Why this match</p>
          <p className="mt-1 text-sm text-ink-700">{candidate.reasoning_summary}</p>
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <ul className="flex flex-wrap gap-2">
          {Object.entries(candidate.profile_urls).map(([kind, url]) =>
            url ? (
              <li key={kind}>
                <a href={url} target="_blank" rel="noreferrer noopener">
                  <Badge>{SOURCE_LABELS[kind] ?? kind}</Badge>
                </a>
              </li>
            ) : null,
          )}
          {candidate.has_resume && (
            <li>
              <Badge tone="emerald">Resume</Badge>
            </li>
          )}
        </ul>
        <button
          type="button"
          onClick={onOpen}
          className="rounded-lg border border-indigo-200 px-3 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-50"
        >
          Open candidate
        </button>
      </div>
    </article>
  )
}
