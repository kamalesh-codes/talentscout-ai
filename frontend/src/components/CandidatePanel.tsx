import { useEffect, useState } from 'react'
import { API_BASE, getCandidate, uploadResume } from '../api'
import { Badge, ConfidenceTag, DemoTag, ScoreDial, SourceLink } from './common'
import type { CandidateDetail } from '../types'

export default function CandidatePanel({
  candidateId,
  onClose,
  onChanged,
}: {
  candidateId: string
  onClose: () => void
  onChanged: () => void
}) {
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getCandidate(candidateId).then(setCandidate).catch((err) => setError(String(err)))
  }, [candidateId])

  async function attachResume(file: File | undefined) {
    if (!file) return
    await uploadResume(file, { candidateId })
    setCandidate(await getCandidate(candidateId))
    onChanged()
  }

  const evaluation = candidate?.evaluation ?? {}
  const profile = candidate?.profile ?? {}

  return (
    <aside className="fixed inset-y-0 right-0 z-20 w-full max-w-2xl overflow-y-auto border-l border-slate-200 bg-white shadow-2xl">
      <header className="sticky top-0 flex items-start justify-between gap-4 border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-xl font-semibold text-ink-900">{candidate?.name ?? 'Loading…'}</h2>
            {candidate?.match_label && <Badge tone="indigo">{candidate.match_label}</Badge>}
            {candidate?.demo_data && <DemoTag />}
          </div>
          <p className="mt-1 text-sm text-ink-700">{candidate?.headline}</p>
        </div>
        <div className="flex items-center gap-4">
          {candidate && <ScoreDial score={candidate.fit_score} />}
          <button type="button" onClick={onClose} className="text-sm text-ink-500 hover:text-ink-900">
            Close
          </button>
        </div>
      </header>

      {error && <p className="px-6 py-4 text-sm text-rose-600">{error}</p>}

      {candidate && (
        <div className="space-y-8 px-6 py-6">
          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Summary</h3>
            <p className="mt-2 text-sm text-ink-700">{evaluation.reasoning_summary || '—'}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {evaluation.recruiter_recommendation && <Badge tone="indigo">{evaluation.recruiter_recommendation}</Badge>}
              {evaluation.confidence && <ConfidenceTag value={evaluation.confidence} />}
              {profile.location?.value && (
                <Badge>
                  {profile.location.value} ({profile.location.confidence})
                </Badge>
              )}
              {profile.experience?.years != null && (
                <Badge>
                  {profile.experience.years} yrs ({profile.experience.confidence})
                </Badge>
              )}
            </div>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Evidence-based skills</h3>
            <table className="mt-2 w-full table-fixed border-collapse text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-ink-500">
                  <th className="w-1/5 py-2">Skill</th>
                  <th className="py-2">Evidence</th>
                  <th className="w-1/5 py-2">Confidence</th>
                  <th className="w-1/5 py-2">Source</th>
                </tr>
              </thead>
              <tbody>
                {(profile.skills ?? []).map((skill, index) => (
                  <tr key={`${skill.name}-${index}`} className="border-t border-slate-100 align-top">
                    <td className="py-2 pr-2 font-medium text-ink-900">{skill.name}</td>
                    <td className="py-2 pr-2 text-ink-700">{skill.evidence}</td>
                    <td className="py-2 pr-2">
                      <ConfidenceTag value={skill.confidence} />
                    </td>
                    <td className="py-2 text-xs">
                      <SourceLink url={skill.source_url} label="source" />
                    </td>
                  </tr>
                ))}
                {(profile.skills ?? []).length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-3 text-ink-500">
                      No source-supported skills extracted.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Projects and notable work</h3>
            <ul className="mt-2 space-y-3">
              {(profile.projects ?? []).map((project, index) => (
                <li key={`${project.name}-${index}`} className="rounded-lg border border-slate-200 p-3">
                  <p className="font-medium text-ink-900">{project.name}</p>
                  <p className="mt-1 text-sm text-ink-700">{project.description}</p>
                  {project.impact && <p className="mt-1 text-sm text-ink-500">{project.impact}</p>}
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {(project.technologies ?? []).map((tech) => (
                      <Badge key={tech}>{tech}</Badge>
                    ))}
                    <span className="text-xs">
                      <SourceLink url={project.source_url} label="source" />
                    </span>
                  </div>
                </li>
              ))}
              {(profile.projects ?? []).length === 0 && <li className="text-sm text-ink-500">None found.</li>}
            </ul>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Match breakdown</h3>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {(['matched', 'missing', 'unknown'] as const).map((key) => (
                <div key={key} className="rounded-lg border border-slate-200 p-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">Must-have {key}</p>
                  <ul className="mt-1 space-y-1 text-sm text-ink-700">
                    {(evaluation.must_have_status?.[key] ?? []).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                    {(evaluation.must_have_status?.[key] ?? []).length === 0 && <li className="text-ink-500">—</li>}
                  </ul>
                </div>
              ))}
            </div>
            <ul className="mt-3 space-y-2">
              {(evaluation.strengths ?? []).map((strength, index) => (
                <li key={index} className="rounded-lg bg-slate-50 p-3 text-sm">
                  <p className="font-medium text-ink-900">{strength.point}</p>
                  <p className="text-ink-700">{strength.evidence}</p>
                  <SourceLink url={strength.source_url} label="source" />
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
              Missing or uncertain information
            </h3>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-700">
              {[...(evaluation.gaps_or_unknowns ?? []), ...(profile.uncertainties ?? [])].map((item, index) => (
                <li key={index}>{item}</li>
              ))}
              {(evaluation.gaps_or_unknowns ?? []).length + (profile.uncertainties ?? []).length === 0 && (
                <li className="text-ink-500">None recorded.</li>
              )}
            </ul>
          </section>

          <section>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Sources</h3>
            <ul className="mt-2 space-y-1 text-sm">
              {(profile.source_links ?? []).map((url) => (
                <li key={url}>
                  <SourceLink url={url} />
                </li>
              ))}
            </ul>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
              {candidate.has_resume ? (
                <a
                  className="text-indigo-600 underline underline-offset-2"
                  href={`${API_BASE}/resumes/${candidate.id}`}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  Download uploaded resume
                </a>
              ) : (
                <label className="cursor-pointer text-indigo-600 underline underline-offset-2">
                  Attach a resume
                  <input
                    type="file"
                    accept=".pdf,.txt,.md"
                    className="hidden"
                    onChange={(event) => attachResume(event.target.files?.[0])}
                  />
                </label>
              )}
              {profile.resume_url && !candidate.has_resume && (
                <SourceLink url={profile.resume_url} label="Public resume link" />
              )}
            </div>
          </section>

          <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            AI-assisted recommendation. Recruiter review required.
          </p>
        </div>
      )}
    </aside>
  )
}
