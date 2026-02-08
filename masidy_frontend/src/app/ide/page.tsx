'use client'

import React, { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import {
  IDESidebar,
  AIBuilder,
  FileExplorer,
  CodeEditor,
  Preview,
  IDEToolbar,
  ViewMode,
} from '@/components/ide'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  content?: string
}

function IDEContent() {
  const searchParams = useSearchParams()
  const initialPrompt = searchParams.get('prompt') || undefined
  const initialFlow = searchParams.get('flow') || 'saas'

  const [viewMode, setViewMode] = useState<ViewMode>('split')
  const [files, setFiles] = useState<FileNode[]>([])
  const [selectedFile, setSelectedFile] = useState<string | undefined>()
  const [selectedContent, setSelectedContent] = useState<string | undefined>()
  const [isExecuting, setIsExecuting] = useState(false)
  const [projectName, setProjectName] = useState('New Project')
  const [aiPanelWidth, setAiPanelWidth] = useState(400)

  // Extract project name from prompt
  useEffect(() => {
    if (initialPrompt) {
      const name = initialPrompt
        .toLowerCase()
        .replace(/build|create|make|a|an|the/gi, '')
        .trim()
        .split(' ')
        .slice(0, 3)
        .join('_')
        .replace(/[^a-z0-9_]/g, '')
      setProjectName(name || 'my_project')
    }
  }, [initialPrompt])

  const handleFileSelect = (path: string, content?: string) => {
    setSelectedFile(path)
    setSelectedContent(content)
    if (viewMode === 'preview') {
      setViewMode('code')
    }
  }

  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)
  const [selectedLanguage, setSelectedLanguage] = useState<string>('text')

  const handleFileCreated = useCallback((path: string, content: string, language?: string) => {
    if (language) {
      setSelectedLanguage(language)
    }
    
    setFiles((prev) => {
      const parts = path.split('/')
      const newFiles = JSON.parse(JSON.stringify(prev)) // Deep clone
      
      let current = newFiles
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i]
        const isFile = i === parts.length - 1
        
        const existingIndex = current.findIndex((f: FileNode) => f.name === part)
        
        if (existingIndex >= 0) {
          if (isFile) {
            current[existingIndex].content = content
          } else {
            if (!current[existingIndex].children) {
              current[existingIndex].children = []
            }
            current = current[existingIndex].children!
          }
        } else {
          if (isFile) {
            current.push({ name: part, type: 'file', content })
          } else {
            const newFolder: FileNode = { name: part, type: 'folder', children: [] }
            current.push(newFolder)
            current = newFolder.children!
          }
        }
      }
      
      return newFiles
    })
  }, [])

  const handleProjectCreated = useCallback((projectId: string, name: string) => {
    setCurrentProjectId(projectId)
    setProjectName(name)
  }, [])

  const handleExecutionStart = () => {
    setIsExecuting(true)
  }

  const handleExecutionComplete = (createdFiles: string[]) => {
    setIsExecuting(false)
    if (createdFiles.length > 0) {
      // Select first created file
      const firstFile = files.find((f) => f.type === 'file')
      if (firstFile) {
        setSelectedFile(firstFile.name)
        setSelectedContent(firstFile.content)
      }
    }
  }

  // Resizer logic
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    const startX = e.clientX
    const startWidth = aiPanelWidth

    const handleMouseMove = (e: MouseEvent) => {
      const delta = e.clientX - startX
      const newWidth = Math.max(300, Math.min(600, startWidth + delta))
      setAiPanelWidth(newWidth)
    }

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  return (
    <div className="h-screen flex bg-white overflow-hidden">
      {/* Sidebar */}
      <IDESidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Toolbar */}
        <IDEToolbar
          projectName={projectName}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />

        {/* IDE Layout */}
        <div className="flex-1 flex overflow-hidden">
          {/* AI Builder Panel */}
          <div style={{ width: aiPanelWidth }} className="flex-shrink-0">
            <AIBuilder
              initialPrompt={initialPrompt}
              flow={initialFlow}
              onExecutionStart={handleExecutionStart}
              onExecutionComplete={handleExecutionComplete}
              onFileCreated={handleFileCreated}
              onProjectCreated={handleProjectCreated}
            />
          </div>

          {/* Resizer */}
          <div
            className="resizer"
            onMouseDown={handleMouseDown}
          />

          {/* File Explorer */}
          <div className="w-56 flex-shrink-0">
            <FileExplorer
              files={files}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
          </div>

          {/* Code/Preview Area */}
          <div className="flex-1 flex overflow-hidden">
            {viewMode === 'preview' && (
              <div className="flex-1">
                <Preview
                  isLoading={isExecuting}
                  projectName={projectName}
                />
              </div>
            )}

            {viewMode === 'code' && (
              <div className="flex-1">
                <CodeEditor
                  filename={selectedFile}
                  content={selectedContent}
                />
              </div>
            )}

            {viewMode === 'split' && (
              <>
                <div className="flex-1 border-r border-border">
                  <CodeEditor
                    filename={selectedFile}
                    content={selectedContent}
                  />
                </div>
                <div className="flex-1">
                  <Preview
                    isLoading={isExecuting}
                    projectName={projectName}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function IDEPage() {
  return (
    <Suspense fallback={
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    }>
      <IDEContent />
    </Suspense>
  )
}
