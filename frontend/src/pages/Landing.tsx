import { PrivacyNotice } from '../components/common'

export default function Landing({ onStart }: { onStart: () => void }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-16">
      <p className="text-sm font-medium uppercase tracking-[0.2em] text-indigo-600">TalentScout AI</p>
      <h1 className="mt-4 text-5xl font-semibold leading-tight text-ink-900">
        Evidence-backed candidate discovery.
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-ink-700">
        Paste a job description. A local Qwen 2.5 agent searches public sources — GitHub, portfolios and
        engineering blogs — and DeepSeek R1 scores every candidate against your must-haves, with a source
        link behind each claim.
      </p>
      <div className="mt-10">
        <button
          type="button"
          onClick={onStart}
          className="rounded-lg bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm transition hover:bg-indigo-700"
        >
          Start sourcing
        </button>
      </div>
      <div className="mt-12 grid gap-4 sm:grid-cols-3">
        {[
          ['Public sources only', 'GitHub API, portfolios, blogs and public result links. robots.txt honoured.'],
          ['Explainable scores', '50/20/15/10/5 rubric across must-haves, preferred skills, projects, domain and evidence.'],
          ['Recruiter in control', 'Every claim links to its source; unknowns are labelled, not guessed.'],
        ].map(([title, body]) => (
          <div key={title} className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-ink-900">{title}</h2>
            <p className="mt-2 text-sm text-ink-500">{body}</p>
          </div>
        ))}
      </div>
      <div className="mt-10">
        <PrivacyNotice />
      </div>
    </div>
  )
}
