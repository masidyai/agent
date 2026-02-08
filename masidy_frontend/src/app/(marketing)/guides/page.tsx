import Link from 'next/link'

const guides = [
  {
    title: 'Building Your First App',
    description: 'A step-by-step guide to creating your first application with Masidy.',
    time: '10 min read',
    difficulty: 'Beginner',
    href: '/guides/first-app',
  },
  {
    title: 'Working with Templates',
    description: 'How to use and customize pre-built templates for common use cases.',
    time: '8 min read',
    difficulty: 'Beginner',
    href: '/guides/templates',
  },
  {
    title: 'GitHub Integration Setup',
    description: 'Connect Masidy to your GitHub account for seamless code management.',
    time: '5 min read',
    difficulty: 'Intermediate',
    href: '/guides/github',
  },
  {
    title: 'Database Configuration',
    description: 'Set up and configure databases for your Masidy projects.',
    time: '12 min read',
    difficulty: 'Intermediate',
    href: '/guides/database',
  },
  {
    title: 'Deploying to Production',
    description: 'Deploy your application to Vercel, Railway, or custom infrastructure.',
    time: '15 min read',
    difficulty: 'Intermediate',
    href: '/guides/deployment',
  },
  {
    title: 'Custom Agent Configuration',
    description: 'Advanced guide to customizing AI agent behavior and prompts.',
    time: '20 min read',
    difficulty: 'Advanced',
    href: '/guides/agents',
  },
  {
    title: 'Team Collaboration',
    description: 'Set up team workspaces and collaborate on projects.',
    time: '10 min read',
    difficulty: 'Intermediate',
    href: '/guides/teams',
  },
  {
    title: 'API Integration',
    description: 'Use the Masidy API to automate workflows and integrate with other tools.',
    time: '15 min read',
    difficulty: 'Advanced',
    href: '/guides/api',
  },
]

const difficultyColors: Record<string, string> = {
  Beginner: 'bg-green-100 text-green-800',
  Intermediate: 'bg-yellow-100 text-yellow-800',
  Advanced: 'bg-red-100 text-red-800',
}

export default function GuidesPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Guides</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Step-by-step tutorials to help you get the most out of Masidy.
          </p>
        </div>
      </section>

      {/* Guides Grid */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {guides.map((guide, index) => (
              <Link
                key={index}
                href={guide.href}
                className="block p-6 border border-gray-200 rounded-xl hover:border-black transition group"
              >
                <div className="flex items-center gap-3 mb-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${difficultyColors[guide.difficulty]}`}>
                    {guide.difficulty}
                  </span>
                  <span className="text-sm text-gray-500">{guide.time}</span>
                </div>
                <h3 className="text-xl font-semibold mb-2 group-hover:underline">{guide.title}</h3>
                <p className="text-gray-600">{guide.description}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Help Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Need help?</h2>
          <p className="text-gray-600 mb-8">
            Can't find what you're looking for? Our team is here to help.
          </p>
          <Link
            href="/contact"
            className="inline-block px-8 py-4 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
          >
            Contact Support
          </Link>
        </div>
      </section>
    </div>
  )
}
