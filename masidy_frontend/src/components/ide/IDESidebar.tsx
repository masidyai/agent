'use client'

import React from 'react'
import Link from 'next/link'
import {
  Sparkles,
  User,
  CreditCard,
  Plug,
  Settings,
  Key,
  Database,
  FolderGit2,
  Home,
} from 'lucide-react'

interface SidebarItem {
  icon: React.ElementType
  label: string
  href?: string
  onClick?: () => void
}

const topItems: SidebarItem[] = [
  { icon: Home, label: 'Dashboard', href: '/dashboard' },
  { icon: FolderGit2, label: 'Projects', href: '/dashboard/projects' },
]

const bottomItems: SidebarItem[] = [
  { icon: User, label: 'Profile', href: '/dashboard/profile' },
  { icon: CreditCard, label: 'Plan', href: '/dashboard/billing' },
  { icon: Plug, label: 'Integrations', href: '/dashboard/integrations' },
  { icon: Key, label: 'API Keys', href: '/dashboard/api-keys' },
  { icon: Database, label: 'Connections', href: '/dashboard/connections' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
]

export function IDESidebar() {
  return (
    <aside className="ide-sidebar">
      {/* Logo */}
      <Link
        href="/"
        className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center mb-4"
      >
        <Sparkles className="w-5 h-5 text-white" />
      </Link>

      {/* Top Items */}
      <div className="flex flex-col gap-1">
        {topItems.map((item) => (
          <Link
            key={item.label}
            href={item.href || '#'}
            className="ide-sidebar-item"
            title={item.label}
          >
            <item.icon className="w-5 h-5" />
          </Link>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Bottom Items */}
      <div className="flex flex-col gap-1">
        {bottomItems.map((item) => (
          <Link
            key={item.label}
            href={item.href || '#'}
            className="ide-sidebar-item"
            title={item.label}
          >
            <item.icon className="w-5 h-5" />
          </Link>
        ))}
      </div>
    </aside>
  )
}
