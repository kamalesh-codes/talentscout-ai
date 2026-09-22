import { useEffect, useState } from 'react'
import { getRun, subscribeToRun } from '../api'
import { Badge } from '../components/common'
import { STAGES } from './JobIntake'
import type { ProgressEvent, RunProgress } from '../types'

export default function Progress({ runId, onDone }: { runId: string; onDone: () => void }) {
  const [events, setEvents] = useState<ProgressEvent[]>([])
  const [run, setRun] = useState<RunProgress | null>(null)

  useEffect(() => {
    const close = subscribeToRun(runId, (event) => setEvents((current) => [...current, event]))
    const poll = window.setInterval(async () => {
      try {
        const progress = await getRun(runId)
        setRun(progress)
        if (progress.status === 'completed' || progress.status === 'failed') {
          window.clearInterval(poll)
          close()
          if (progress.status === 'completed') onDone()
        }
      } catch {
        /* keep polling */
      }
    }, 2000)
    return () => {
      window.clearInterval(poll)
      close()
    }
  }, [runId, onDone])

  const currentIndex = STAGES.findIndex((stage) => stage.key === run?.stage)
  const reachedIndex = run?.stage === 'done' ? STAGES.length : currentIndex

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-ink-900">Sourcing candidates…</h1>
      <p className="mt-1 text-sm text-ink-500">
        Qwen 2.5 researches public sources; DeepSeek R1 scores each candidate. Local CPU inference can take
        several minutes per candidate.
      </p>

      <ol className="mt-8 space-y-3">
        {STAGES.map((stage, index) => {
          const state = index < reachedIndex ? 'done' : index === reachedIndex ? 'active' : 'pending'
          return (
            <li key={stage.key} className="flex items-center gap-3">
              <span
                className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold ${
                  state === 'done'
                    ? 'bg-indigo-600 text-white'
                    : state === 'active'
                      ? 'bg-indigo-100 text-indigo-700 ring-2 ring-indigo-400'
                      : 'bg-slate-100 text-ink-500'
                }`}
              >
                {index + 1}
              </span>
              <span className={state === 'pending' ? 'text-ink-500' : 'text-ink-900'}>{stage.label}</span>
              {state === 'active' && <Badge tone="indigo">in progress</Badge>}
            </li>
          )
        })}
      </ol>

      {run?.demo_data && (
        <p className="mt-6">
          <Badge tone="amber">Demo data — online retrieval or local models unavailable</Badge>
        </p>
      )}
      {run?.error && <p className="mt-6 text-sm text-rose-600">{run.error}</p>}

      <div className="mt-8 max-h-72 overflow-auto rounded-xl border border-slate-200 bg-white p-4 text-xs text-ink-700">
        {events.length === 0 && <p className="text-ink-500">Waiting for the agent…</p>}
        {events.map((event, index) => (
          <p key={index} className="border-b border-slate-100 py-1 last:border-0">
            <span className="font-medium text-ink-900">{event.stage}</span> — {event.message}
            {event.queries && <span className="block pl-2 text-ink-500">{event.queries.join(' · ')}</span>}
          </p>
        ))}
      </div>

      <button
        type="button"
        onClick={onDone}
        className="mt-6 text-sm text-indigo-600 underline underline-offset-2"
      >
        View results so far
      </button>
    </div>
  )
}
