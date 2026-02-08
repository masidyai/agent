import Link from 'next/link'

const team = [
  { name: 'Alex Chen', role: 'CEO & Co-founder', image: '/team/alex.jpg' },
  { name: 'Sarah Johnson', role: 'CTO & Co-founder', image: '/team/sarah.jpg' },
  { name: 'Michael Park', role: 'Head of AI', image: '/team/michael.jpg' },
  { name: 'Emily Davis', role: 'Head of Product', image: '/team/emily.jpg' },
]

const values = [
  {
    title: 'Developer First',
    description: 'We build tools that developers love. Every feature is designed with developer experience in mind.',
    icon: '💻',
  },
  {
    title: 'Quality Over Speed',
    description: 'We don\'t just generate code fast—we generate code that\'s maintainable, tested, and production-ready.',
    icon: '✨',
  },
  {
    title: 'Transparency',
    description: 'We\'re open about how our AI works, its limitations, and what it can and cannot do.',
    icon: '🔍',
  },
  {
    title: 'Continuous Learning',
    description: 'Our AI learns from every interaction to provide better results over time.',
    icon: '📈',
  },
]

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">About Masidy</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            We're on a mission to make software development accessible to everyone through AI.
          </p>
        </div>
      </section>

      {/* Story */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <h2 className="text-3xl font-bold mb-8">Our Story</h2>
          <div className="prose prose-lg">
            <p>
              Masidy was founded in 2023 with a simple idea: what if AI could handle the tedious parts 
              of software development, freeing developers to focus on creativity and problem-solving?
            </p>
            <p>
              Our founders, experienced software engineers and AI researchers, saw that modern AI 
              could do more than just autocomplete code. It could understand requirements, plan 
              architectures, write tests, and even deploy applications.
            </p>
            <p>
              Today, Masidy's multi-agent system helps thousands of developers build production-ready 
              applications faster than ever before. We're just getting started.
            </p>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Our Values</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl mb-4">{value.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                <p className="text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Our Team</h2>
          <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {team.map((member, index) => (
              <div key={index} className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
                  <span className="text-3xl">👤</span>
                </div>
                <h3 className="font-semibold">{member.name}</h3>
                <p className="text-sm text-gray-600">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-black text-white">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Join Us</h2>
          <p className="text-gray-400 mb-8">We're hiring! Help us build the future of development.</p>
          <Link
            href="/careers"
            className="inline-block px-8 py-4 bg-white text-black rounded-lg font-medium hover:bg-gray-100 transition"
          >
            View Open Positions
          </Link>
        </div>
      </section>
    </div>
  )
}
