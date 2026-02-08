import Link from 'next/link'

const positions = [
  {
    title: 'Senior Backend Engineer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-time',
    href: '/careers/senior-backend',
  },
  {
    title: 'ML/AI Engineer',
    department: 'AI Research',
    location: 'Remote',
    type: 'Full-time',
    href: '/careers/ml-engineer',
  },
  {
    title: 'Senior Frontend Engineer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-time',
    href: '/careers/senior-frontend',
  },
  {
    title: 'Developer Relations',
    department: 'Marketing',
    location: 'Remote',
    type: 'Full-time',
    href: '/careers/devrel',
  },
  {
    title: 'Product Designer',
    department: 'Design',
    location: 'Remote',
    type: 'Full-time',
    href: '/careers/product-designer',
  },
]

const benefits = [
  { title: 'Remote First', description: 'Work from anywhere in the world', icon: '🌍' },
  { title: 'Competitive Salary', description: 'Top-of-market compensation', icon: '💰' },
  { title: 'Equity', description: 'Meaningful ownership in the company', icon: '📈' },
  { title: 'Health & Wellness', description: 'Comprehensive health coverage', icon: '🏥' },
  { title: 'Learning Budget', description: '$2,000/year for courses and conferences', icon: '📚' },
  { title: 'Home Office', description: 'Allowance for equipment setup', icon: '🖥️' },
]

export default function CareersPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Join Our Team</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Help us build the future of AI-powered development. We're looking for passionate 
            people who want to make a difference.
          </p>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Why Masidy?</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {benefits.map((benefit, index) => (
              <div key={index} className="text-center p-6">
                <div className="text-4xl mb-4">{benefit.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Open Positions */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Open Positions</h2>
          <div className="max-w-3xl mx-auto space-y-4">
            {positions.map((position, index) => (
              <Link
                key={index}
                href={position.href}
                className="block p-6 bg-white border border-gray-200 rounded-xl hover:border-black transition group"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold group-hover:underline">{position.title}</h3>
                    <p className="text-gray-600">{position.department}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">{position.location}</p>
                    <p className="text-sm text-gray-500">{position.type}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* No Fit? */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Don't see a fit?</h2>
          <p className="text-gray-600 mb-8">
            We're always looking for talented people. Send us your resume and we'll keep you in mind.
          </p>
          <Link
            href="/contact"
            className="inline-block px-8 py-4 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
          >
            Get in Touch
          </Link>
        </div>
      </section>
    </div>
  )
}
