'use client'

import React from 'react'
import {
  GitBranch,
  Share2,
  Globe,
  Download,
  Code2,
  Monitor,
  Columns,
  MoreHorizontal,
} from 'lucide-react'
import { Button } from '@/components/ui'

export type ViewMode = 'preview' | 'code' | 'split'

interface IDEToolbarProps {
  projectName?: string
  viewMode: ViewMode
  onViewModeChange: (mode: ViewMode) => void
  onGitConnect?: () => void
  onShare?: () => void
  onPublish?: () => void
  onDownload?: () => void
}

export function IDEToolbar({
  projectName = 'New Project',
  viewMode,
  onViewModeChange,
  onGitConnect,
  onShare,
  onPublish,
  onDownload,
}: IDEToolbarProps) {
  const ViewButton = ({
    mode,
    icon: Icon,
    label,
  }: {
    mode: ViewMode
    icon: React.ElementType
    label: string
  }) => (
    <button
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors ${
        viewMode === mode
          ? 'bg-primary text-white'
          : 'hover:bg-surface text-secondary'
      }`}
      onClick={() => onViewModeChange(mode)}
    >
      <Icon className="w-4 h-4" />
      <span className="hidden sm:inline">{label}</span>
    </button>
  )

  return (
    <div className="h-12 bg-white border-b border-border flex items-center justify-between px-4">
      {/* Left - Project Info */}
      <div className="flex items-center gap-4">
        <h1 className="font-semibold">{projectName}</h1>
        <span className="text-xs text-secondary px-2 py-0.5 bg-surface rounded">
          Draft
        </span>
      </div>

      {/* Center - View Toggle */}
      <div className="flex items-center gap-1 bg-surface rounded-lg p-1">
        <ViewButton mode="preview" icon={Monitor} label="Preview" />
        <ViewButton mode="code" icon={Code2} label="Code" />
        <ViewButton mode="split" icon={Columns} label="Split" />
      </div>

      {/* Right - Actions */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={onGitConnect} className="gap-2">
          <GitBranch className="w-4 h-4" />
          <span className="hidden md:inline">Git</span>
        </Button>

        <Button variant="ghost" size="sm" onClick={onShare} className="gap-2">
          <Share2 className="w-4 h-4" />
          <span className="hidden md:inline">Share</span>
        </Button>

        <Button variant="ghost" size="sm" onClick={onPublish} className="gap-2">
          <Globe className="w-4 h-4" />
          <span className="hidden md:inline">Publish</span>
        </Button>

        <Button variant="secondary" size="sm" onClick={onDownload} className="gap-2">
          <Download className="w-4 h-4" />
          <span className="hidden md:inline">Export</span>
        </Button>

        <button className="p-2 hover:bg-surface rounded-lg transition-colors">
          <MoreHorizontal className="w-4 h-4 text-secondary" />
        </button>
      </div>
    </div>
  )
}
