const releases = [
  {
    version: 'v1.2.0',
    date: 'February 8, 2024',
    changes: [
      { type: 'feature', text: 'Multi-agent collaboration system with Builder, Reviewer, Tester, Fixer, and Deployer' },
      { type: 'feature', text: 'Real-time WebSocket streaming for live updates' },
      { type: 'feature', text: 'One-click deployment to Vercel and Railway' },
      { type: 'improvement', text: 'Improved code generation accuracy by 40%' },
      { type: 'fix', text: 'Fixed file explorer not updating after generation' },
    ],
  },
  {
    version: 'v1.1.0',
    date: 'January 25, 2024',
    changes: [
      { type: 'feature', text: 'GitHub integration for direct repository pushes' },
      { type: 'feature', text: 'AI-powered code review and suggestions' },
      { type: 'feature', text: 'Team collaboration features' },
      { type: 'improvement', text: 'Faster project generation (2x speed improvement)' },
      { type: 'fix', text: 'Fixed authentication token refresh issues' },
    ],
  },
  {
    version: 'v1.0.0',
    date: 'January 10, 2024',
    changes: [
      { type: 'feature', text: 'Initial release of Masidy AI Agent Platform' },
      { type: 'feature', text: 'AI-powered full-stack code generation' },
      { type: 'feature', text: 'Real-time preview panel' },
      { type: 'feature', text: 'Multiple framework support (Next.js, React, FastAPI, Express)' },
      { type: 'feature', text: 'Database schema generation' },
    ],
  },
]

const typeStyles = {
  feature: 'bg-green-100 text-green-800',
  improvement: 'bg-blue-100 text-blue-800',
  fix: 'bg-yellow-100 text-yellow-800',
}

const typeLabels = {
  feature: 'New',
  improvement: 'Improved',
  fix: 'Fixed',
}

export default function ChangelogPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Changelog</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Stay up to date with the latest features, improvements, and fixes.
          </p>
        </div>
      </section>

      {/* Releases */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <div className="space-y-12">
            {releases.map((release, index) => (
              <div key={index} className="relative">
                <div className="flex items-center mb-4">
                  <span className="text-2xl font-bold">{release.version}</span>
                  <span className="ml-4 text-gray-500">{release.date}</span>
                </div>
                <div className="space-y-3">
                  {release.changes.map((change, changeIndex) => (
                    <div key={changeIndex} className="flex items-start">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${typeStyles[change.type as keyof typeof typeStyles]}`}>
                        {typeLabels[change.type as keyof typeof typeLabels]}
                      </span>
                      <span className="ml-3 text-gray-700">{change.text}</span>
                    </div>
                  ))}
                </div>
                {index < releases.length - 1 && (
                  <div className="mt-12 border-b border-gray-200" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
