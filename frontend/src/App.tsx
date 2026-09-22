import { useCallback, useState } from 'react'
import Dashboard from './pages/Dashboard'
import JobIntake from './pages/JobIntake'
import Landing from './pages/Landing'
import Progress from './pages/Progress'

type View = 'landing' | 'intake' | 'progress' | 'results'

export default function App() {
  const [view, setView] = useState<View>('landing')
  const [runId, setRunId] = useState<string | undefined>()

  const showResults = useCallback(() => setView('results'), [])

  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <button type="button" onClick={() => setView('landing')} className="text-sm font-semibold text-ink-900">
            TalentScout <span className="text-indigo-600">AI</span>
          </button>
          <div className="flex gap-4 text-sm text-ink-500">
            <button type="button" onClick={() => setView('intake')} className="hover:text-ink-900">
              Job intake
            </button>
            <button type="button" onClick={showResults} className="hover:text-ink-900">
              Results
            </button>
          </div>
        </div>
      </nav>

      {view === 'landing' && <Landing onStart={() => setView('intake')} />}
      {view === 'intake' && (
        <JobIntake
          onStarted={(id) => {
            setRunId(id)
            setView('progress')
          }}
        />
      )}
      {view === 'progress' && runId && <Progress runId={runId} onDone={showResults} />}
      {view === 'results' && <Dashboard runId={runId} onNewSearch={() => setView('intake')} />}
    </div>
  )
}
