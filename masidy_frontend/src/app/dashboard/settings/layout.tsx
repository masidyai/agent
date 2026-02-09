'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { User, Settings, Plug, Key } from 'lucide-react'

const settingsNav = [
  { icon: User, label: 'Profile', href: '/dashboard/settings/profile' },
  { icon: Settings, label: 'General', href: '/dashboard/settings/general' },
  { icon: Plug, label: 'Integrations', href: '/dashboard/settings/integrations' },
  { icon: Key, label: 'API Keys', href: '/dashboard/settings/api-keys' },
]

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">Settings</h1>
          <p className="text-secondary">Manage your account settings and preferences</p>
        </div>

        <div className="flex gap-8">
          {/* Settings Navigation */}
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {settingsNav.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-secondary hover:bg-surface hover:text-primary'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                )
              })}
            </nav>
          </aside>

          {/* Settings Content */}
          <main className="flex-1 bg-surface rounded-lg border border-border p-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
