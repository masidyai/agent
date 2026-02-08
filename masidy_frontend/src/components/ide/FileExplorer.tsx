'use client'

import React, { useState } from 'react'
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  FileJson,
  File,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  content?: string
}

interface FileExplorerProps {
  files: FileNode[]
  onFileSelect?: (path: string, content?: string) => void
  selectedFile?: string
}

function getFileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'py':
    case 'js':
    case 'ts':
    case 'tsx':
    case 'jsx':
      return FileCode
    case 'json':
      return FileJson
    case 'md':
    case 'txt':
      return FileText
    default:
      return File
  }
}

function FileTreeItem({
  node,
  path,
  depth,
  onFileSelect,
  selectedFile,
}: {
  node: FileNode
  path: string
  depth: number
  onFileSelect?: (path: string, content?: string) => void
  selectedFile?: string
}) {
  const [isOpen, setIsOpen] = useState(depth < 2)
  const fullPath = path ? `${path}/${node.name}` : node.name
  const isSelected = selectedFile === fullPath

  if (node.type === 'folder') {
    return (
      <div>
        <button
          className={`w-full flex items-center gap-2 px-2 py-1.5 hover:bg-surface rounded text-sm transition-colors ${
            isSelected ? 'bg-surface' : ''
          }`}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? (
            <ChevronDown className="w-3 h-3 text-secondary" />
          ) : (
            <ChevronRight className="w-3 h-3 text-secondary" />
          )}
          {isOpen ? (
            <FolderOpen className="w-4 h-4 text-yellow-500" />
          ) : (
            <Folder className="w-4 h-4 text-yellow-500" />
          )}
          <span className="truncate">{node.name}</span>
        </button>
        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <FileTreeItem
                key={child.name}
                node={child}
                path={fullPath}
                depth={depth + 1}
                onFileSelect={onFileSelect}
                selectedFile={selectedFile}
              />
            ))}
          </div>
        )}
      </div>
    )
  }

  const Icon = getFileIcon(node.name)

  return (
    <button
      className={`w-full flex items-center gap-2 px-2 py-1.5 hover:bg-surface rounded text-sm transition-colors ${
        isSelected ? 'bg-primary/10 text-primary' : ''
      }`}
      style={{ paddingLeft: `${depth * 12 + 20}px` }}
      onClick={() => onFileSelect?.(fullPath, node.content)}
    >
      <Icon className="w-4 h-4 text-secondary" />
      <span className="truncate">{node.name}</span>
    </button>
  )
}

export function FileExplorer({ files, onFileSelect, selectedFile }: FileExplorerProps) {
  return (
    <div className="h-full bg-white border-r border-border flex flex-col">
      {/* Header */}
      <div className="h-10 border-b border-border px-4 flex items-center">
        <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider">
          Explorer
        </h3>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto py-2">
        {files.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <Folder className="w-8 h-8 text-secondary mx-auto mb-2" />
            <p className="text-sm text-secondary">No files yet</p>
            <p className="text-xs text-muted mt-1">
              Files will appear here as they are created
            </p>
          </div>
        ) : (
          files.map((node) => (
            <FileTreeItem
              key={node.name}
              node={node}
              path=""
              depth={0}
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))
        )}
      </div>
    </div>
  )
}
