import Link from 'next/link'

const examples = [
  {
    title: 'Task Management SaaS',
    description: 'Full-stack application with user authentication, teams, projects, and real-time updates.',
    tags: ['Next.js', 'PostgreSQL', 'Auth', 'Real-time'],
    image: '/examples/task-manager.png',
    href: '/signup?template=task-management',
  },
  {
    title: 'REST API Service',
    description: 'Production-ready REST API with CRUD operations, validation, authentication, and documentation.',
    tags: ['FastAPI', 'PostgreSQL', 'OpenAPI', 'JWT'],
    image: '/examples/api-service.png',
    href: '/signup?template=rest-api',
  },
  {
    title: 'E-commerce Backend',
    description: 'Complete backend with products, orders, payments, and inventory management.',
    tags: ['Node.js', 'Stripe', 'PostgreSQL', 'Redis'],
    image: '/examples/ecommerce.png',
    href: '/signup?template=ecommerce',
  },
  {
    title: 'Chat Application',
    description: 'Real-time chat with WebSockets, message history, and user presence.',
    tags: ['React', 'Socket.io', 'MongoDB', 'Redis'],
    image: '/examples/chat.png',
    href: '/signup?template=chat',
  },
  {
    title: 'Blog Platform',
    description: 'Full-featured blog with markdown support, comments, and SEO optimization.',
    tags: ['Next.js', 'MDX', 'PostgreSQL', 'SEO'],
    image: '/examples/blog.png',
    href: '/signup?template=blog',
  },
  {
    title: 'Analytics Dashboard',
    description: 'Data visualization dashboard with charts, filters, and real-time updates.',
    tags: ['React', 'D3.js', 'PostgreSQL', 'Charts'],
    image: '/examples/analytics.png',
    href: '/signup?template=analytics',
  },
]

export default function ExamplesPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Ready-Made Examples
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Start with production-ready templates and customize them for your needs. Each example is fully functional and deployable.
          </p>
        </div>
      </section>

      {/* Examples Grid */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {examples.map((example, index) => (
              <div key={index} className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition group">
                <div className="h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <div className="text-6xl opacity-50">📦</div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-2">{example.title}</h3>
                  <p className="text-gray-600 mb-4">{example.description}</p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {example.tags.map((tag, tagIndex) => (
                      <span key={tagIndex} className="px-2 py-1 bg-gray-100 rounded text-sm text-gray-600">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <Link 
                    href={example.href}
                    className="inline-flex items-center text-black font-medium group-hover:underline"
                  >
                    Try this example
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Have a custom idea?</h2>
          <p className="text-gray-600 mb-8">Describe any application and Masidy will build it for you.</p>
          <Link href="/signup" className="inline-block px-8 py-4 bg-black text-white rounded-lg text-lg font-medium hover:bg-gray-800 transition">
            Start Building
          </Link>
        </div>
      </section>
    </div>
  )
}
