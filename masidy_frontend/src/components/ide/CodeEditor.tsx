'use client'

import React from 'react'
import { FileCode, Copy, Download } from 'lucide-react'

interface CodeEditorProps {
  filename?: string
  content?: string
  language?: string
}

export function CodeEditor({ filename, content, language }: CodeEditorProps) {
  const copyToClipboard = () => {
    if (content) {
      navigator.clipboard.writeText(content)
    }
  }

  if (!filename || !content) {
    return (
      <div className="h-full bg-surface flex items-center justify-center">
        <div className="text-center">
          <FileCode className="w-12 h-12 text-secondary mx-auto mb-3" />
          <p className="text-secondary">Select a file to view its contents</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Tab Bar */}
      <div className="h-10 border-b border-border flex items-center justify-between px-2">
        <div className="flex items-center gap-2 bg-surface px-3 py-1.5 rounded-t border-b-2 border-primary">
          <FileCode className="w-4 h-4 text-secondary" />
          <span className="text-sm font-medium">{filename}</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={copyToClipboard}
            className="p-1.5 hover:bg-surface rounded transition-colors"
            title="Copy content"
          >
            <Copy className="w-4 h-4 text-secondary" />
          </button>
          <button
            className="p-1.5 hover:bg-surface rounded transition-colors"
            title="Download file"
          >
            <Download className="w-4 h-4 text-secondary" />
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-auto">
        <pre className="p-4 text-sm font-mono leading-relaxed">
          <code>{content}</code>
        </pre>
      </div>

      {/* Status Bar */}
      <div className="h-6 border-t border-border bg-surface px-4 flex items-center justify-between text-xs text-secondary">
        <span>{language || 'Plain Text'}</span>
        <span>{content.split('\n').length} lines</span>
      </div>
    </div>
  )
}
