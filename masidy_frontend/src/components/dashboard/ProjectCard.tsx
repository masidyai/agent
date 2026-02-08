'use client'

import React from 'react'
import Link from 'next/link'
import { Layers, Server, RefreshCw, MoreVertical, ExternalLink } from 'lucide-react'

interface ProjectCardProps {
  id: string
  name: string
  type: 'saas' | 'api' | 'refactor'
  status: 'completed' | 'in_progress' | 'failed'
  createdAt: string
  stepsCompleted?: number
  stepsTotal?: number
}

const typeIcons = {
  saas: Layers,
  api: Server,
  refactor: RefreshCw,
}

const typeLabels = {
  saas: 'SaaS App',
  api: 'API Service',
  refactor: 'Refactor',
}

const statusColors = {
  completed: 'bg-green-100 text-green-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  failed: 'bg-red-100 text-red-700',
}

const statusLabels = {
  completed: 'Completed',
  in_progress: 'In Progress',
  failed: 'Failed',
}

export function ProjectCard({
  id,
  name,
  type,
  status,
  createdAt,
  stepsCompleted,
  stepsTotal,
}: ProjectCardProps) {
  const Icon = typeIcons[type]

  return (
    <div className="bg-white rounded-xl border border-border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-surface rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">{name}</h3>
            <p className="text-sm text-secondary">{typeLabels[type]}</p>
          </div>
        </div>
        <button className="p-2 hover:bg-surface rounded-lg transition-colors">
          <MoreVertical className="w-4 h-4 text-secondary" />
        </button>
      </div>

      <div className="flex items-center justify-between mb-4">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]}`}>
          {statusLabels[status]}
        </span>
        {stepsCompleted !== undefined && stepsTotal !== undefined && (
          <span className="text-sm text-secondary">
            {stepsCompleted}/{stepsTotal} steps
          </span>
        )}
      </div>

      {status === 'in_progress' && stepsCompleted !== undefined && stepsTotal !== undefined && (
        <div className="mb-4">
          <div className="h-2 bg-surface rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${(stepsCompleted / stepsTotal) * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-sm">
        <span className="text-secondary">
          {new Date(createdAt).toLocaleDateString()}
        </span>
        <Link
          href={`/ide?project=${id}`}
          className="flex items-center gap-1 text-primary hover:underline"
        >
          Open <ExternalLink className="w-3 h-3" />
        </Link>
      </div>
    </div>
  )
}
