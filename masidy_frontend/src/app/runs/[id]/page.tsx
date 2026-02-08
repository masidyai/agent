'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Step {
  id: string
  name: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  order: number
  logs?: string
}

interface FileNode {
  name: string
  path: string
  type: 'file' | 'directory'
  children?: FileNode[]
}

interface Run {
  id: string
  project_id: string
  prompt: string
  status: string
  plan: string
  created_at: string
}

export default function RunPage() {
  const params = useParams()
  const router = useRouter()
  const runId = params.id as string

  const [run, setRun] = useState<Run | null>(null)
  const [steps, setSteps] = useState<Step[]>([])
  const [files, setFiles] = useState<FileNode[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [building, setBuilding] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const [chatInput, setChatInput] = useState('')
  const [viewMode, setViewMode] = useState<'code' | 'preview' | 'split'>('split')

  const logsEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    fetchRun()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [runId])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const fetchRun = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      const [runRes, stepsRes, filesRes] = await Promise.all([
        fetch(`${API_URL}/api/runs/${runId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/runs/${runId}/steps`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/runs/${runId}/files`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ])

      if (runRes.ok) {
        const runData = await runRes.json()
        setRun(runData)
        
        if (runData.status === 'in_progress') {
          connectWebSocket()
        }
      }

      if (stepsRes.ok) {
        const stepsData = await stepsRes.json()
        setSteps(stepsData)
      }

      if (filesRes.ok) {
        const filesData = await filesRes.json()
        setFiles(filesData)
      }
    } catch (err) {
      console.error('Failed to fetch run:', err)
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    const wsUrl = API_URL.replace('http', 'ws')
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(`${wsUrl}/ws/runs/${runId}?token=${token}`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'step_update') {
        setSteps(prev => prev.map(s => 
          s.id === data.step_id ? { ...s, status: data.status } : s
        ))
      } else if (data.type === 'log') {
        setLogs(prev => [...prev, data.message])
      } else if (data.type === 'file_created') {
        fetchFiles()
      } else if (data.type === 'run_completed') {
        setBuilding(false)
        setRun(prev => prev ? { ...prev, status: 'completed' } : null)
        fetchFiles()
      }
    }

    ws.onerror = () => {
      console.error('WebSocket error')
    }

    wsRef.current = ws
  }

  const fetchFiles = async () => {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${API_URL}/api/runs/${runId}/files`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      setFiles(data)
    }
  }

  const loadFile = async (path: string) => {
    setSelectedFile(path)
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API_URL}/api/runs/${runId}/files/${encodeURIComponent(path)}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setFileContent(data.content)
      }
    } catch (err) {
      console.error('Failed to load file:', err)
    }
  }

  const startBuilding = async () => {
    setBuilding(true)
    setLogs([])
    
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${API_URL}/api/runs/${runId}/start`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      })
      
      connectWebSocket()
    } catch (err) {
      console.error('Failed to start build:', err)
      setBuilding(false)
    }
  }

  const sendMessage = async () => {
    if (!chatInput.trim()) return
    
    setLogs(prev => [...prev, `You: ${chatInput}`])
    const message = chatInput
    setChatInput('')

    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${API_URL}/api/runs/${runId}/message`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      })
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'in_progress': return '⏳'
      case 'failed': return '❌'
      default: return '⭕'
    }
  }

  const getFileIcon = (name: string) => {
    if (name.endsWith('.ts') || name.endsWith('.tsx')) return '📘'
    if (name.endsWith('.js') || name.endsWith('.jsx')) return '📒'
    if (name.endsWith('.py')) return '🐍'
    if (name.endsWith('.json')) return '📋'
    if (name.endsWith('.md')) return '📝'
    if (name.endsWith('.css') || name.endsWith('.scss')) return '🎨'
    if (name.endsWith('.html')) return '🌐'
    return '📄'
  }

  const renderFileTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => (
      <div key={node.path}>
        <button
          onClick={() => node.type === 'file' && loadFile(node.path)}
          className={`w-full text-left px-2 py-1 text-sm hover:bg-gray-100 rounded flex items-center gap-2 ${
            selectedFile === node.path ? 'bg-gray-100' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
        >
          {node.type === 'directory' ? '📁' : getFileIcon(node.name)}
          {node.name}
        </button>
        {node.children && renderFileTree(node.children, depth + 1)}
      </div>
    ))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-black border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-600">Loading project...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
          </Link>
          <span className="text-gray-300">|</span>
          <span className="font-medium">{run?.prompt?.slice(0, 50)}...</span>
          <span className={`px-2 py-0.5 text-xs rounded ${
            run?.status === 'completed' ? 'bg-green-100 text-green-700' :
            run?.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
            'bg-gray-100 text-gray-700'
          }`}>
            {run?.status}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="flex border border-gray-200 rounded-lg overflow-hidden">
            {(['code', 'split', 'preview'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1.5 text-sm ${
                  viewMode === mode ? 'bg-black text-white' : 'hover:bg-gray-100'
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          <button className="px-4 py-1.5 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">
            Export
          </button>
          <button className="px-4 py-1.5 bg-black text-white rounded-lg text-sm hover:bg-gray-800">
            Deploy
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - AI Builder */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white">🤖</span>
              </div>
              <div>
                <h3 className="font-semibold">AI Builder</h3>
                <p className="text-xs text-gray-500">
                  {building ? 'Building...' : 'Ready to build'}
                </p>
              </div>
            </div>
          </div>

          {/* Steps */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2 mb-4">
              {steps.length > 0 ? (
                steps.map((step) => (
                  <div key={step.id} className="flex items-start gap-2 p-2 rounded hover:bg-gray-50">
                    <span>{getStepIcon(step.status)}</span>
                    <div>
                      <p className="text-sm font-medium">{step.name}</p>
                      {step.description && (
                        <p className="text-xs text-gray-500">{step.description}</p>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p className="mb-2">No plan generated yet</p>
                  <p className="text-sm">Click "Start Building" to begin</p>
                </div>
              )}
            </div>

            {/* Logs */}
            {logs.length > 0 && (
              <div className="mt-4 p-3 bg-gray-900 rounded-lg max-h-40 overflow-y-auto">
                {logs.map((log, i) => (
                  <p key={i} className="text-xs text-gray-300 font-mono">{log}</p>
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="p-4 border-t border-gray-200">
            {!building && run?.status !== 'completed' && (
              <button
                onClick={startBuilding}
                className="w-full py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition flex items-center justify-center gap-2"
              >
                ▶ Start Building
              </button>
            )}
            
            {building && (
              <div className="flex items-center justify-center gap-2 py-3 text-gray-600">
                <div className="animate-spin h-4 w-4 border-2 border-black border-t-transparent rounded-full" />
                Building...
              </div>
            )}

            {run?.status === 'completed' && (
              <div className="text-center py-3 text-green-600 font-medium">
                ✅ Build Complete
              </div>
            )}

            {/* Chat Input */}
            <div className="mt-4 flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask a question..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black"
              />
              <button
                onClick={sendMessage}
                className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
              >
                →
              </button>
            </div>
          </div>
        </div>

        {/* Center - Code Editor */}
        {(viewMode === 'code' || viewMode === 'split') && (
          <div className={`${viewMode === 'split' ? 'flex-1' : 'flex-1'} flex`}>
            {/* File Explorer */}
            <div className="w-56 bg-white border-r border-gray-200 overflow-y-auto">
              <div className="p-3 border-b border-gray-200">
                <h4 className="text-xs font-semibold text-gray-500 uppercase">Explorer</h4>
              </div>
              <div className="p-2">
                {files.length > 0 ? (
                  renderFileTree(files)
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <div className="text-3xl mb-2">📂</div>
                    <p className="text-sm">No files yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Code View */}
            <div className="flex-1 bg-gray-900 overflow-hidden flex flex-col">
              {selectedFile ? (
                <>
                  <div className="h-10 bg-gray-800 px-4 flex items-center text-gray-400 text-sm border-b border-gray-700">
                    {selectedFile}
                  </div>
                  <pre className="flex-1 overflow-auto p-4 text-sm text-gray-300 font-mono">
                    {fileContent || 'Loading...'}
                  </pre>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <div className="text-4xl mb-2">📝</div>
                    <p>Select a file to view its contents</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Right - Preview */}
        {(viewMode === 'preview' || viewMode === 'split') && (
          <div className={`${viewMode === 'split' ? 'w-1/2' : 'flex-1'} bg-white border-l border-gray-200 flex flex-col`}>
            <div className="h-10 bg-gray-50 px-4 flex items-center justify-between border-b border-gray-200">
              <span className="text-sm font-medium">Preview</span>
              <button className="text-sm text-gray-500 hover:text-gray-700">↻ Refresh</button>
            </div>
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-4xl mb-2">🖥️</div>
                <p>Preview will appear here</p>
                <p className="text-sm mt-1">Start building to see your app</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
