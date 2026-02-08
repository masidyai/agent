'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'

const mainNav = [
  { name: 'Dashboard', href: '/dashboard', icon: '🏠' },
  { name: 'New Project', href: '/dashboard/new-project', icon: '➕' },
  { name: 'My Projects', href: '/dashboard/projects', icon: '📁' },
]

const settingsNav = [
  { name: 'Profile', href: '/dashboard/settings/profile', icon: '👤' },
  { name: 'Plan & Billing', href: '/dashboard/billing', icon: '💳' },
  { name: 'Integrations', href: '/dashboard/settings/integrations', icon: '🔗' },
  { name: 'API Keys', href: '/dashboard/settings/api-keys', icon: '🔑' },
  { name: 'Settings', href: '/dashboard/settings/general', icon: '⚙️' },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [user, setUser] = useState<{ name: string; email: string; plan: string } | null>(null)

  useEffect(() => {
    // Get user from localStorage or API
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    } else {
      setUser({ name: 'User', email: 'user@example.com', plan: 'Free Plan' })
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <span className="text-xl font-bold">Masidy</span>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-4">
          <div className="mb-6">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
              Main
            </p>
            <ul className="space-y-1">
              {mainNav.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center px-3 py-2 rounded-lg transition ${
                      pathname === item.href
                        ? 'bg-black text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-3">{item.icon}</span>
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
              Settings
            </p>
            <ul className="space-y-1">
              {settingsNav.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center px-3 py-2 rounded-lg transition ${
                      pathname === item.href
                        ? 'bg-black text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-3">{item.icon}</span>
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-gray-600 font-medium">
                {user?.name?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">{user?.name || 'User'}</p>
              <p className="text-xs text-gray-500">{user?.plan || 'Free Plan'}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
