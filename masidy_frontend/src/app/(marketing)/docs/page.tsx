import Link from 'next/link'

const sections = [
  {
    title: 'Getting Started',
    items: [
      { title: 'Introduction', description: 'Learn what Masidy is and how it works', href: '/docs#introduction' },
      { title: 'Quick Start', description: 'Build your first application in 5 minutes', href: '/docs#quickstart' },
      { title: 'Core Concepts', description: 'Understand projects, runs, and agents', href: '/docs#concepts' },
    ],
  },
  {
    title: 'Features',
    items: [
      { title: 'AI Code Generation', description: 'How the AI generates code from prompts', href: '/docs#generation' },
      { title: 'Multi-Agent System', description: 'Learn about Builder, Reviewer, Tester, Fixer, Deployer', href: '/docs#agents' },
      { title: 'Real-Time Preview', description: 'See your app as it\'s being built', href: '/docs#preview' },
    ],
  },
  {
    title: 'Integrations',
    items: [
      { title: 'GitHub', description: 'Connect and push to GitHub repositories', href: '/docs#github' },
      { title: 'Deployment', description: 'Deploy to Vercel, Railway, and more', href: '/docs#deployment' },
      { title: 'Databases', description: 'PostgreSQL, MySQL, MongoDB support', href: '/docs#databases' },
    ],
  },
]

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Documentation</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Everything you need to build amazing applications with Masidy.
          </p>
          <div className="max-w-md mx-auto">
            <input
              type="text"
              placeholder="Search documentation..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-12">
            {sections.map((section, index) => (
              <div key={index}>
                <h2 className="text-xl font-bold mb-6">{section.title}</h2>
                <div className="space-y-4">
                  {section.items.map((item, itemIndex) => (
                    <Link
                      key={itemIndex}
                      href={item.href}
                      className="block p-4 border border-gray-200 rounded-lg hover:border-black transition"
                    >
                      <h3 className="font-semibold mb-1">{item.title}</h3>
                      <p className="text-sm text-gray-600">{item.description}</p>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6 max-w-4xl">
          <article className="prose prose-lg max-w-none">
            <h2 id="introduction">Introduction</h2>
            <p>
              Masidy is an AI-powered development platform that transforms natural language descriptions into 
              production-ready applications. Using a multi-agent system, Masidy handles everything from code 
              generation to testing and deployment.
            </p>

            <h2 id="quickstart">Quick Start</h2>
            <ol>
              <li><strong>Create an Account:</strong> Sign up at masidy.com</li>
              <li><strong>Describe Your App:</strong> Tell Masidy what you want to build</li>
              <li><strong>Review the Plan:</strong> The AI will generate a development plan</li>
              <li><strong>Start Building:</strong> Click "Start Building" to generate your app</li>
              <li><strong>Deploy:</strong> One-click deploy to your preferred platform</li>
            </ol>

            <h2 id="concepts">Core Concepts</h2>
            <h3>Projects</h3>
            <p>
              A project represents an application you're building. It contains all the source code, 
              configuration, and deployment settings.
            </p>

            <h3>Runs</h3>
            <p>
              A run is a single execution of the AI agents. Each run generates code based on your 
              prompt and the current state of the project.
            </p>

            <h3>Agents</h3>
            <p>
              Masidy uses five specialized AI agents that work together:
            </p>
            <ul>
              <li><strong>Builder:</strong> Generates code based on requirements</li>
              <li><strong>Reviewer:</strong> Reviews code for quality and best practices</li>
              <li><strong>Tester:</strong> Writes and runs tests</li>
              <li><strong>Fixer:</strong> Fixes bugs and issues</li>
              <li><strong>Deployer:</strong> Handles deployment configuration</li>
            </ul>
          </article>
        </div>
      </section>
    </div>
  )
}
