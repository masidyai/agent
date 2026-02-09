'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  User,
  CreditCard,
  Plug,
  Settings,
  Key,
  FolderGit2,
  Sparkles,
  LayoutDashboard,
  Plus,
} from 'lucide-react'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: Plus, label: 'New Project', href: '/ide' },
  { icon: FolderGit2, label: 'My Projects', href: '/dashboard/projects' },
]

const settingsItems = [
  { icon: User, label: 'Profile', href: '/dashboard/settings/profile' },
  { icon: CreditCard, label: 'Plan & Billing', href: '/dashboard/billing' },
  { icon: Plug, label: 'Integrations', href: '/dashboard/settings/integrations' },
  { icon: Key, label: 'API Keys', href: '/dashboard/settings/api-keys' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings/general' },
]

export function DashboardSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-surface border-r border-border min-h-screen">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-border">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold">Masidy</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="p-4">
        <div className="mb-6">
          <p className="px-3 mb-2 text-xs font-semibold text-secondary uppercase tracking-wider">
            Main
          </p>
          <ul className="space-y-1">
            {menuItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-secondary hover:bg-white hover:text-primary'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>

        <div>
          <p className="px-3 mb-2 text-xs font-semibold text-secondary uppercase tracking-wider">
            Settings
          </p>
          <ul className="space-y-1">
            {settingsItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-secondary hover:bg-white hover:text-primary'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
      </nav>

      {/* User */}
      <div className="absolute bottom-0 left-0 w-64 p-4 border-t border-border bg-surface">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-semibold">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">User</p>
            <p className="text-sm text-secondary truncate">Free Plan</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
