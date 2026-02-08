import Link from 'next/link'

const features = [
  {
    title: 'AI-Powered Code Generation',
    description: 'Generate production-ready code from natural language descriptions. Our AI understands context and produces clean, maintainable code.',
    icon: '✨',
  },
  {
    title: 'Full-Stack Generation',
    description: 'Create complete applications with frontend, backend, database schemas, and API endpoints - all from a single prompt.',
    icon: '🏗️',
  },
  {
    title: 'Multi-Agent System',
    description: 'Five specialized AI agents work together: Builder, Reviewer, Tester, Fixer, and Deployer for comprehensive development.',
    icon: '🤖',
  },
  {
    title: 'Real-Time Preview',
    description: 'See your application come to life as it\'s being built. Live preview updates as code is generated.',
    icon: '👁️',
  },
  {
    title: 'GitHub Integration',
    description: 'Seamlessly connect to your GitHub repositories. Push code, create branches, and manage your projects.',
    icon: '🔗',
  },
  {
    title: 'One-Click Deploy',
    description: 'Deploy to Vercel, Railway, or your own infrastructure with a single click. Zero configuration required.',
    icon: '🚀',
  },
  {
    title: 'Smart Code Review',
    description: 'AI-powered code review identifies issues, suggests improvements, and ensures best practices are followed.',
    icon: '🔍',
  },
  {
    title: 'Automatic Testing',
    description: 'Generate comprehensive test suites automatically. Unit tests, integration tests, and E2E tests included.',
    icon: '✅',
  },
  {
    title: 'Database Support',
    description: 'Support for PostgreSQL, MySQL, SQLite, MongoDB, and more. Automatic schema generation and migrations.',
    icon: '🗄️',
  },
]

export default function FeaturesPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Powerful Features for<br />Modern Development
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Everything you need to build, test, and deploy production-ready applications powered by AI.
          </p>
          <Link href="/signup" className="inline-block px-8 py-4 bg-black text-white rounded-lg text-lg font-medium hover:bg-gray-800 transition">
            Start Building Free
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="p-6 border border-gray-200 rounded-xl hover:shadow-lg transition">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-black text-white">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to transform your development workflow?</h2>
          <p className="text-gray-400 mb-8">Join thousands of developers building faster with Masidy.</p>
          <Link href="/signup" className="inline-block px-8 py-4 bg-white text-black rounded-lg text-lg font-medium hover:bg-gray-100 transition">
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  )
}
