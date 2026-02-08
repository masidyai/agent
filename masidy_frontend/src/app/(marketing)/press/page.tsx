import Link from 'next/link'

const pressReleases = [
  {
    title: 'Masidy Launches AI-Powered Development Platform',
    date: 'February 8, 2024',
    source: 'Press Release',
    href: '#',
  },
  {
    title: 'Masidy Raises $10M Series A to Accelerate AI Development Tools',
    date: 'January 15, 2024',
    source: 'Press Release',
    href: '#',
  },
]

const mediaKit = [
  { name: 'Logo Package', description: 'PNG, SVG, and EPS formats', href: '#' },
  { name: 'Brand Guidelines', description: 'Colors, typography, and usage', href: '#' },
  { name: 'Product Screenshots', description: 'High-resolution images', href: '#' },
  { name: 'Founder Photos', description: 'Professional headshots', href: '#' },
]

export default function PressPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Press</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            News, press releases, and media resources.
          </p>
        </div>
      </section>

      {/* Press Contact */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="bg-gray-50 p-8 rounded-xl mb-12">
            <h2 className="text-2xl font-bold mb-4">Press Contact</h2>
            <p className="text-gray-600 mb-4">
              For press inquiries, please contact our communications team:
            </p>
            <a href="mailto:press@masidy.com" className="text-black font-medium hover:underline">
              press@masidy.com
            </a>
          </div>

          {/* Press Releases */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold mb-6">Press Releases</h2>
            <div className="space-y-4">
              {pressReleases.map((release, index) => (
                <Link
                  key={index}
                  href={release.href}
                  className="block p-6 border border-gray-200 rounded-xl hover:border-black transition"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold">{release.title}</h3>
                      <p className="text-sm text-gray-500">{release.source}</p>
                    </div>
                    <span className="text-sm text-gray-500">{release.date}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Media Kit */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Media Kit</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {mediaKit.map((item, index) => (
                <Link
                  key={index}
                  href={item.href}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:border-black transition"
                >
                  <span className="text-2xl mr-4">📁</span>
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-sm text-gray-500">{item.description}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
