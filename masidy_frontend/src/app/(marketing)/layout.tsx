'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-xl font-bold">Masidy</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <div className="relative group">
                <button className="text-gray-600 hover:text-black transition">Product</button>
                <div className="absolute top-full left-0 mt-2 w-48 bg-white shadow-lg rounded-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link href="/features" className="block px-4 py-2 hover:bg-gray-50">Features</Link>
                  <Link href="/examples" className="block px-4 py-2 hover:bg-gray-50">Examples</Link>
                  <Link href="/pricing" className="block px-4 py-2 hover:bg-gray-50">Pricing</Link>
                  <Link href="/changelog" className="block px-4 py-2 hover:bg-gray-50">Changelog</Link>
                </div>
              </div>
              <div className="relative group">
                <button className="text-gray-600 hover:text-black transition">Resources</button>
                <div className="absolute top-full left-0 mt-2 w-48 bg-white shadow-lg rounded-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link href="/docs" className="block px-4 py-2 hover:bg-gray-50">Documentation</Link>
                  <Link href="/api-reference" className="block px-4 py-2 hover:bg-gray-50">API Reference</Link>
                  <Link href="/guides" className="block px-4 py-2 hover:bg-gray-50">Guides</Link>
                  <Link href="/blog" className="block px-4 py-2 hover:bg-gray-50">Blog</Link>
                </div>
              </div>
              <div className="relative group">
                <button className="text-gray-600 hover:text-black transition">Company</button>
                <div className="absolute top-full left-0 mt-2 w-48 bg-white shadow-lg rounded-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link href="/about" className="block px-4 py-2 hover:bg-gray-50">About</Link>
                  <Link href="/careers" className="block px-4 py-2 hover:bg-gray-50">Careers</Link>
                  <Link href="/contact" className="block px-4 py-2 hover:bg-gray-50">Contact</Link>
                  <Link href="/press" className="block px-4 py-2 hover:bg-gray-50">Press</Link>
                </div>
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login" className="text-gray-600 hover:text-black transition">
                Sign in
              </Link>
              <Link href="/signup" className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition">
                Get Started
              </Link>
            </div>

            {/* Mobile menu button */}
            <button 
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden mt-4 pb-4 border-t border-gray-100 pt-4">
              <div className="space-y-2">
                <Link href="/features" className="block py-2 text-gray-600">Features</Link>
                <Link href="/pricing" className="block py-2 text-gray-600">Pricing</Link>
                <Link href="/docs" className="block py-2 text-gray-600">Docs</Link>
                <Link href="/about" className="block py-2 text-gray-600">About</Link>
                <Link href="/login" className="block py-2 text-gray-600">Sign in</Link>
                <Link href="/signup" className="block py-2 bg-black text-white rounded-lg text-center">Get Started</Link>
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Main Content */}
      <main className="pt-20">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-100 mt-20">
        <div className="container mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">M</span>
                </div>
                <span className="text-xl font-bold">Masidy</span>
              </Link>
              <p className="mt-4 text-sm text-gray-500">
                AI-powered development platform that builds production-ready applications.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-500">
                <li><Link href="/features" className="hover:text-black">Features</Link></li>
                <li><Link href="/examples" className="hover:text-black">Examples</Link></li>
                <li><Link href="/pricing" className="hover:text-black">Pricing</Link></li>
                <li><Link href="/changelog" className="hover:text-black">Changelog</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-gray-500">
                <li><Link href="/docs" className="hover:text-black">Documentation</Link></li>
                <li><Link href="/api-reference" className="hover:text-black">API Reference</Link></li>
                <li><Link href="/guides" className="hover:text-black">Guides</Link></li>
                <li><Link href="/blog" className="hover:text-black">Blog</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-500">
                <li><Link href="/about" className="hover:text-black">About</Link></li>
                <li><Link href="/careers" className="hover:text-black">Careers</Link></li>
                <li><Link href="/contact" className="hover:text-black">Contact</Link></li>
                <li><Link href="/press" className="hover:text-black">Press</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-500">
                <li><Link href="/privacy" className="hover:text-black">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-black">Terms</Link></li>
                <li><Link href="/security" className="hover:text-black">Security</Link></li>
                <li><Link href="/cookies" className="hover:text-black">Cookies</Link></li>
              </ul>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-gray-200 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">© 2024 Masidy. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="https://twitter.com/masidy" className="text-gray-400 hover:text-black">
                <span className="sr-only">Twitter</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="https://github.com/masidy" className="text-gray-400 hover:text-black">
                <span className="sr-only">GitHub</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
