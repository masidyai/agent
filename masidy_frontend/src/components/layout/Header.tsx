'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui'

const navItems = [
  { name: 'Features', href: '/#features' },
  { name: 'Examples', href: '/#examples' },
  { name: 'Pricing', href: '/#pricing' },
  { name: 'Docs', href: '/docs' },
]

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  const isLandingPage = pathname === '/'

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-border">
      <div className="container-custom">
        <div className="flex items-center justify-between h-16 px-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">Masidy</span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8">
            {isLandingPage && navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="text-secondary hover:text-primary transition-colors font-medium"
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">Dashboard</Button>
            </Link>
            <Link href="/ide">
              <Button size="sm">Start Building</Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border py-4 px-4">
            <nav className="flex flex-col gap-4">
              {isLandingPage && navItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="text-secondary hover:text-primary transition-colors font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
              <hr className="border-border" />
              <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="secondary" className="w-full">Dashboard</Button>
              </Link>
              <Link href="/ide" onClick={() => setMobileMenuOpen(false)}>
                <Button className="w-full">Start Building</Button>
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
