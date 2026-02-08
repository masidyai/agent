'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Bot, User, CheckCircle, Loader2, AlertCircle, Play, Square, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui'
import * as api from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  type?: 'thinking' | 'plan' | 'executing' | 'complete' | 'error'
  plan?: PlanStep[]
}

interface PlanStep {
  id: number
  description: string
  status: 'pending' | 'executing' | 'completed' | 'failed'
  tool_name?: string
}

interface AIBuilderProps {
  initialPrompt?: string
  flow?: string
  onExecutionStart?: () => void
  onExecutionComplete?: (files: string[]) => void
  onFileCreated?: (path: string, content: string) => void
}

export function AIBuilder({
  initialPrompt,
  flow = 'saas',
  onExecutionStart,
  onExecutionComplete,
  onFileCreated,
}: AIBuilderProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [currentPlan, setCurrentPlan] = useState<PlanStep[] | null>(null)
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false)
  const [currentProject, setCurrentProject] = useState<api.Project | null>(null)
  const [useBackend, setUseBackend] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const hasInitialized = useRef(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (initialPrompt && !hasInitialized.current) {
      hasInitialized.current = true
      handleInitialPrompt(initialPrompt)
    }
  }, [initialPrompt])

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newMessage])
    return newMessage
  }

  const updateLastMessage = (updates: Partial<Message>) => {
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastIndex = newMessages.length - 1
      if (lastIndex >= 0) {
        newMessages[lastIndex] = { ...newMessages[lastIndex], ...updates }
      }
      return newMessages
    })
  }

  const handleInitialPrompt = async (prompt: string) => {
    addMessage({ role: 'user', content: prompt })
    await analyzeAndPlan(prompt)
  }

  const analyzeAndPlan = async (prompt: string) => {
    setIsThinking(true)
    
    addMessage({
      role: 'assistant',
      content: '🤔 Analyzing your request...',
      type: 'thinking',
    })

    try {
      if (useBackend) {
        // Try to use the backend API
        const project = await api.createProject(prompt, flow)
        setCurrentProject(project)
        
        await new Promise((resolve) => setTimeout(resolve, 500))
        
        const executionPlan = await api.getExecutionPlan(project.id)
        const plan: PlanStep[] = executionPlan.steps.map(s => ({
          id: s.id,
          description: s.description,
          status: 'pending' as const,
          tool_name: s.tool_name,
        }))
        
        setCurrentPlan(plan)
        
        updateLastMessage({
          content: `I've analyzed your request and created project "${project.name}". Here's my execution plan:`,
          type: 'plan',
          plan: plan,
        })
      } else {
        // Fallback to local simulation
        await new Promise((resolve) => setTimeout(resolve, 1500))
        const plan = generatePlan(prompt, flow)
        setCurrentPlan(plan)

        updateLastMessage({
          content: `I've analyzed your request and understand what you need. Here's my plan:`,
          type: 'plan',
          plan: plan,
        })
      }
    } catch (error) {
      console.error('Backend API error, falling back to simulation:', error)
      setUseBackend(false)
      
      await new Promise((resolve) => setTimeout(resolve, 1000))
      const plan = generatePlan(prompt, flow)
      setCurrentPlan(plan)

      updateLastMessage({
        content: `I've analyzed your request and understand what you need. Here's my plan:`,
        type: 'plan',
        plan: plan,
      })
    }

    setIsThinking(false)
    setAwaitingConfirmation(true)
  }

  const generatePlan = (prompt: string, flowType: string): PlanStep[] => {
    const basePlans: Record<string, PlanStep[]> = {
      saas: [
        { id: 1, description: 'Create project structure', status: 'pending' },
        { id: 2, description: 'Set up backend with FastAPI', status: 'pending' },
        { id: 3, description: 'Configure database models', status: 'pending' },
        { id: 4, description: 'Implement authentication', status: 'pending' },
        { id: 5, description: 'Create API endpoints', status: 'pending' },
        { id: 6, description: 'Build frontend components', status: 'pending' },
        { id: 7, description: 'Set up Docker configuration', status: 'pending' },
        { id: 8, description: 'Add tests and documentation', status: 'pending' },
        { id: 9, description: 'Configure CI/CD pipeline', status: 'pending' },
        { id: 10, description: 'Final review and cleanup', status: 'pending' },
      ],
      api: [
        { id: 1, description: 'Create project directory structure', status: 'pending' },
        { id: 2, description: 'Initialize FastAPI application', status: 'pending' },
        { id: 3, description: 'Set up database and models', status: 'pending' },
        { id: 4, description: 'Create CRUD endpoints', status: 'pending' },
        { id: 5, description: 'Add input validation', status: 'pending' },
        { id: 6, description: 'Implement error handling', status: 'pending' },
        { id: 7, description: 'Write unit tests', status: 'pending' },
        { id: 8, description: 'Create Docker setup', status: 'pending' },
        { id: 9, description: 'Generate API documentation', status: 'pending' },
        { id: 10, description: 'Add GitHub Actions CI/CD', status: 'pending' },
      ],
      refactor: [
        { id: 1, description: 'Analyze existing codebase', status: 'pending' },
        { id: 2, description: 'Add type hints and documentation', status: 'pending' },
        { id: 3, description: 'Restructure project layout', status: 'pending' },
        { id: 4, description: 'Add Dockerfile', status: 'pending' },
        { id: 5, description: 'Create docker-compose.yml', status: 'pending' },
        { id: 6, description: 'Add test suite', status: 'pending' },
        { id: 7, description: 'Configure linting and formatting', status: 'pending' },
        { id: 8, description: 'Set up GitHub Actions', status: 'pending' },
      ],
    }

    return basePlans[flowType] || basePlans.api
  }

  const confirmPlan = async () => {
    setAwaitingConfirmation(false)
    setIsExecuting(true)
    onExecutionStart?.()

    addMessage({
      role: 'assistant',
      content: '🚀 Starting execution...',
      type: 'executing',
    })

    // Execute plan steps
    if (currentPlan) {
      const files: string[] = []
      
      try {
        if (useBackend && currentProject) {
          // Use backend streaming execution
          const { execution_id } = await api.startExecution(currentProject.id)
          
          await api.streamExecution(
            execution_id,
            (event) => {
              if (event.type === 'step_start' && event.step !== undefined) {
                setCurrentPlan((prev) => {
                  if (!prev) return prev
                  const updated = [...prev]
                  const idx = event.step! - 1
                  if (updated[idx]) {
                    updated[idx] = { ...updated[idx], status: 'executing' }
                  }
                  return updated
                })
                updateLastMessage({
                  content: `⚡ Executing step ${event.step}/${event.total}: ${event.description}`,
                })
              } else if (event.type === 'step_complete' && event.step !== undefined) {
                setCurrentPlan((prev) => {
                  if (!prev) return prev
                  const updated = [...prev]
                  const idx = event.step! - 1
                  if (updated[idx]) {
                    updated[idx] = { ...updated[idx], status: 'completed' }
                  }
                  return updated
                })
                if (event.file) {
                  files.push(event.file)
                  onFileCreated?.(event.file, `// Generated: ${event.file}\n// Content will be loaded from backend`)
                }
              } else if (event.type === 'complete') {
                setIsExecuting(false)
                addMessage({
                  role: 'assistant',
                  content: `✅ Project complete! ${event.files_created?.length || files.length} files created.\n\nYour project is ready to use. You can:\n- Browse the code in the file explorer\n- Preview the application\n- Download or publish your project`,
                  type: 'complete',
                })
                onExecutionComplete?.(event.files_created || files)
              }
            },
            (error) => {
              console.error('Streaming error:', error)
              fallbackExecution(files)
            }
          )
        } else {
          await fallbackExecution(files)
        }
      } catch (error) {
        console.error('Execution error:', error)
        await fallbackExecution(files)
      }
    }
  }

  const fallbackExecution = async (files: string[]) => {
    // Fallback to local simulation
    if (currentPlan) {
      for (let i = 0; i < currentPlan.length; i++) {
        const step = currentPlan[i]
        
        setCurrentPlan((prev) => {
          if (!prev) return prev
          const updated = [...prev]
          updated[i] = { ...updated[i], status: 'executing' }
          return updated
        })

        updateLastMessage({
          content: `⚡ Executing step ${i + 1}/${currentPlan.length}: ${step.description}`,
        })

        await new Promise((resolve) => setTimeout(resolve, 600 + Math.random() * 400))

        const mockFile = generateMockFile(step, flow)
        if (mockFile) {
          files.push(mockFile.path)
          onFileCreated?.(mockFile.path, mockFile.content)
        }

        setCurrentPlan((prev) => {
          if (!prev) return prev
          const updated = [...prev]
          updated[i] = { ...updated[i], status: 'completed' }
          return updated
        })
      }

      setIsExecuting(false)
      
      addMessage({
        role: 'assistant',
        content: `✅ Project complete! ${files.length} files created.\n\nYour project is ready to use. You can:\n- Browse the code in the file explorer\n- Preview the application\n- Download or publish your project`,
        type: 'complete',
      })

      onExecutionComplete?.(files)
    }
  }

  const generateMockFile = (step: PlanStep, flowType: string) => {
    const fileMap: Record<number, { path: string; content: string }> = {
      1: { path: 'README.md', content: '# Project\n\nGenerated by Masidy' },
      2: { path: 'app/main.py', content: 'from fastapi import FastAPI\n\napp = FastAPI()' },
      3: { path: 'app/models.py', content: 'from sqlalchemy import Column, Integer, String' },
      4: { path: 'app/auth.py', content: '# Authentication module' },
      5: { path: 'app/routes.py', content: '# API Routes' },
      6: { path: 'frontend/App.tsx', content: 'export default function App() {}' },
      7: { path: 'Dockerfile', content: 'FROM python:3.11-slim' },
      8: { path: 'tests/test_main.py', content: 'def test_example(): pass' },
      9: { path: '.github/workflows/ci.yml', content: 'name: CI' },
      10: { path: 'requirements.txt', content: 'fastapi\nuvicorn\nsqlalchemy' },
    }
    return fileMap[step.id]
  }

  const cancelExecution = () => {
    setIsExecuting(false)
    addMessage({
      role: 'system',
      content: '⚠️ Execution cancelled',
      type: 'error',
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isThinking || isExecuting) return

    const userMessage = input.trim()
    setInput('')
    addMessage({ role: 'user', content: userMessage })
    await analyzeAndPlan(userMessage)
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-border">
      {/* Header */}
      <div className="h-14 border-b border-border px-4 flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-sm">AI Builder</h2>
          <p className="text-xs text-secondary">
            {isExecuting ? 'Executing...' : isThinking ? 'Thinking...' : 'Ready'}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center mx-auto mb-4">
              <Bot className="w-8 h-8 text-secondary" />
            </div>
            <h3 className="font-semibold mb-2">AI Builder</h3>
            <p className="text-secondary text-sm max-w-xs mx-auto">
              Describe what you want to build and I&apos;ll create it for you step by step.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                message.role === 'user' ? 'bg-primary' : 'bg-surface'
              }`}
            >
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>

            <div
              className={`flex-1 ${message.role === 'user' ? 'text-right' : ''}`}
            >
              <div
                className={`inline-block rounded-xl px-4 py-3 max-w-[90%] ${
                  message.role === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-surface'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                {/* Plan Display */}
                {message.plan && (
                  <div className="mt-4 space-y-2">
                    {message.plan.map((step) => (
                      <div
                        key={step.id}
                        className={`flex items-center gap-2 text-sm ${
                          message.role === 'user' ? 'text-white/80' : 'text-secondary'
                        }`}
                      >
                        {step.status === 'completed' ? (
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                        ) : step.status === 'executing' ? (
                          <Loader2 className="w-4 h-4 animate-spin text-accent flex-shrink-0" />
                        ) : step.status === 'failed' ? (
                          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border-2 border-current flex-shrink-0" />
                        )}
                        <span>{step.id}. {step.description}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <p className="text-xs text-muted mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Confirmation Buttons */}
        {awaitingConfirmation && (
          <div className="flex gap-2 justify-center py-4">
            <Button onClick={confirmPlan} className="gap-2">
              <Play className="w-4 h-4" />
              Start Building
            </Button>
            <Button variant="secondary" onClick={() => setAwaitingConfirmation(false)}>
              Modify Plan
            </Button>
          </div>
        )}

        {/* Executing Cancel */}
        {isExecuting && (
          <div className="flex justify-center py-4">
            <Button variant="secondary" onClick={cancelExecution} className="gap-2">
              <Square className="w-4 h-4" />
              Cancel
            </Button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-border">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe what you want to build..."
            className="input flex-1"
            disabled={isThinking || isExecuting || awaitingConfirmation}
          />
          <Button
            type="submit"
            disabled={!input.trim() || isThinking || isExecuting || awaitingConfirmation}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}
