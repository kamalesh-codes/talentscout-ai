import type { ReactNode } from 'react'
import type { Confidence } from '../types'

export function Badge({ children, tone = 'slate' }: { children: ReactNode; tone?: 'slate' | 'indigo' | 'amber' | 'emerald' | 'rose' }) {
  const tones = {
    slate: 'bg-slate-100 text-ink-700 ring-slate-200',
    indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-200',
    amber: 'bg-amber-50 text-amber-800 ring-amber-200',
    emerald: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    rose: 'bg-rose-50 text-rose-700 ring-rose-200',
  }
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${tones[tone]}`}>
      {children}
    </span>
  )
}

export function ConfidenceTag({ value }: { value: Confidence }) {
  if (!value) return null
  const tone = value === 'verified' || value === 'high' ? 'emerald' : value === 'unknown' ? 'rose' : 'amber'
  return <Badge tone={tone}>{value}</Badge>
}

export function DemoTag() {
  return <Badge tone="amber">Demo data</Badge>
}

export function SourceLink({ url, label }: { url: string; label?: string }) {
  if (!url) return <span className="text-ink-500">no source</span>
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer noopener"
      className="text-indigo-600 underline decoration-indigo-300 underline-offset-2 hover:text-indigo-800 break-all"
    >
      {label ?? url}
    </a>
  )
}

export function ScoreDial({ score }: { score: number }) {
  const tone = score >= 75 ? 'text-emerald-600' : score >= 50 ? 'text-indigo-600' : 'text-ink-500'
  return (
    <div className="flex flex-col items-center">
      <span className={`text-3xl font-semibold tabular-nums ${tone}`}>{Math.round(score)}</span>
      <span className="text-[11px] uppercase tracking-wide text-ink-500">fit score</span>
    </div>
  )
}

export function PrivacyNotice() {
  return (
    <p className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-xs leading-relaxed text-ink-500">
      <span className="font-medium text-ink-700">Privacy &amp; fairness:</span> TalentScout AI uses public,
      non-gated sources only. LinkedIn pages are never scraped — discovered profile URLs are shown as links.
      Protected characteristics are never inferred or used in ranking, and missing information is labelled
      unknown rather than penalised. Scores are recommendations, not hiring decisions.
    </p>
  )
}
