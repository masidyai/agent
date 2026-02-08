import Link from 'next/link'

const posts = [
  {
    title: 'Introducing Masidy: AI-Powered Development Platform',
    excerpt: 'Today we\'re excited to announce Masidy, a new way to build production-ready applications using AI.',
    date: 'February 8, 2024',
    author: 'Masidy Team',
    category: 'Announcement',
    href: '/blog/introducing-masidy',
  },
  {
    title: 'How Multi-Agent Systems Build Better Code',
    excerpt: 'Learn how our five specialized AI agents work together to create, review, test, fix, and deploy code.',
    date: 'February 5, 2024',
    author: 'Engineering Team',
    category: 'Technical',
    href: '/blog/multi-agent-systems',
  },
  {
    title: 'Building a SaaS App in Under 10 Minutes',
    excerpt: 'A walkthrough of creating a full-stack task management application using Masidy.',
    date: 'February 1, 2024',
    author: 'Developer Relations',
    category: 'Tutorial',
    href: '/blog/saas-in-10-minutes',
  },
  {
    title: 'The Future of AI-Assisted Development',
    excerpt: 'Our vision for how AI will transform the way developers build software.',
    date: 'January 28, 2024',
    author: 'Masidy Team',
    category: 'Thoughts',
    href: '/blog/future-of-ai-development',
  },
  {
    title: 'Best Practices for AI-Generated Code',
    excerpt: 'Tips and strategies for getting the best results from AI code generation.',
    date: 'January 25, 2024',
    author: 'Engineering Team',
    category: 'Guide',
    href: '/blog/best-practices',
  },
  {
    title: 'Case Study: How Acme Corp Reduced Development Time by 80%',
    excerpt: 'Learn how Acme Corp used Masidy to dramatically speed up their development workflow.',
    date: 'January 20, 2024',
    author: 'Masidy Team',
    category: 'Case Study',
    href: '/blog/acme-case-study',
  },
]

const categoryColors: Record<string, string> = {
  Announcement: 'bg-purple-100 text-purple-800',
  Technical: 'bg-blue-100 text-blue-800',
  Tutorial: 'bg-green-100 text-green-800',
  Thoughts: 'bg-yellow-100 text-yellow-800',
  Guide: 'bg-orange-100 text-orange-800',
  'Case Study': 'bg-pink-100 text-pink-800',
}

export default function BlogPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Blog</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Insights, tutorials, and updates from the Masidy team.
          </p>
        </div>
      </section>

      {/* Blog Posts */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="space-y-8">
            {posts.map((post, index) => (
              <Link
                key={index}
                href={post.href}
                className="block p-6 border border-gray-200 rounded-xl hover:border-black transition group"
              >
                <div className="flex items-center gap-3 mb-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${categoryColors[post.category]}`}>
                    {post.category}
                  </span>
                  <span className="text-sm text-gray-500">{post.date}</span>
                </div>
                <h2 className="text-2xl font-bold mb-2 group-hover:underline">{post.title}</h2>
                <p className="text-gray-600 mb-4">{post.excerpt}</p>
                <p className="text-sm text-gray-500">By {post.author}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-20 bg-black text-white">
        <div className="container mx-auto px-6 text-center max-w-2xl">
          <h2 className="text-3xl font-bold mb-4">Stay Updated</h2>
          <p className="text-gray-400 mb-8">
            Subscribe to our newsletter for the latest updates, tutorials, and insights.
          </p>
          <form className="flex gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-100 transition"
            >
              Subscribe
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}
