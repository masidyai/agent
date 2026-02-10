'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Bot, User, CheckCircle, Loader2, AlertCircle, Play, Square, Sparkles, FileCode } from 'lucide-react'
import { Button } from '@/components/ui'
import * as api from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  type?: 'thinking' | 'planning' | 'plan' | 'executing' | 'complete' | 'error'
  plan?: PlanStep[]
}

interface PlanStep {
  id: number
  description: string
  status: 'pending' | 'executing' | 'completed' | 'failed'
  file_path?: string
}

interface AIBuilderProps {
  initialPrompt?: string
  flow?: string
  onExecutionStart?: () => void
  onExecutionComplete?: (files: string[]) => void
  onFileCreated?: (path: string, content: string, language: string) => void
  onProjectCreated?: (projectId: string, name: string) => void
}

export function AIBuilder({
  initialPrompt,
  flow = 'saas',
  onExecutionStart,
  onExecutionComplete,
  onFileCreated,
  onProjectCreated,
}: AIBuilderProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [currentPlan, setCurrentPlan] = useState<PlanStep[] | null>(null)
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)
  const [currentExecutionId, setCurrentExecutionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const hasInitialized = useRef(false)
  const cleanupRef = useRef<(() => void) | null>(null)

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

  useEffect(() => {
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current()
      }
    }
  }, [])

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).slice(2),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newMessage])
    return newMessage
  }, [])

  const updateLastMessage = useCallback((updates: Partial<Message>) => {
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastIndex = newMessages.length - 1
      if (lastIndex >= 0) {
        newMessages[lastIndex] = { ...newMessages[lastIndex], ...updates }
      }
      return newMessages
    })
  }, [])

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
      const result = await api.planAndExecute(prompt, flow)
      
      setCurrentProjectId(result.project_id)
      setCurrentExecutionId(result.execution_id)
      onProjectCreated?.(result.project_id, result.name)
      
      const plan = await api.getExecutionPlan(result.project_id)
      
      const planSteps: PlanStep[] = plan.steps.map(s => ({
        id: s.id,
        description: s.description,
        status: 'pending' as const,
        file_path: s.file_path,
      }))
      
      setCurrentPlan(planSteps)
      
      updateLastMessage({
        content: `I've analyzed your request and created project "${result.name}". Here's my execution plan with ${plan.total_files} files:`,
        type: 'plan',
        plan: planSteps,
      })
      
      setAwaitingConfirmation(true)
    } catch (error: unknown) {
      console.error('API error:', error)
      
      // Show the actual error instead of falling back to demo mode
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      
      // Check if it's an API key error
      const isApiKeyError = errorMessage.includes('OpenAI') || 
                           errorMessage.includes('API key') || 
                           errorMessage.includes('503')
      
      updateLastMessage({
        content: isApiKeyError 
          ? `❌ **OpenAI API Key Required**\n\nTo generate real projects, you need to configure your OpenAI API key:\n\n1. Add \`OPENAI_API_KEY=sk-your-key\` to your \`.env\` file\n2. Restart the backend server\n3. Try again\n\nGet your API key at: https://platform.openai.com/api-keys`
          : `❌ **Error**: ${errorMessage}\n\nPlease check the backend server is running and try again.`,
        type: 'error',
      })
      
      setIsThinking(false)
      return
    }

    setIsThinking(false)
  }

  // REMOVED: generateLocalPlan function - no more demo mode fallback
  // All project generation now requires real OpenAI API

  const confirmPlan = async () => {
    setAwaitingConfirmation(false)
    setIsExecuting(true)
    onExecutionStart?.()

    addMessage({
      role: 'assistant',
      content: '🚀 Starting AI code generation...',
      type: 'executing',
    })

    if (currentExecutionId) {
      const cleanup = api.streamExecution(
        currentExecutionId,
        (event) => handleExecutionEvent(event),
        (error) => {
          console.error('Streaming error:', error)
          setIsExecuting(false)
          addMessage({
            role: 'system',
            content: `❌ Error: ${error.message}\n\nMake sure the backend server is running with a valid OpenAI API key.`,
            type: 'error',
          })
        },
        () => {
          setIsExecuting(false)
        }
      )
      cleanupRef.current = cleanup
    } else {
      // No execution ID means the API failed - show error instead of demo mode
      setIsExecuting(false)
      addMessage({
        role: 'system',
        content: '❌ Cannot start execution: No execution ID. Please try creating a new project.',
        type: 'error',
      })
    }
  }

  const handleExecutionEvent = (event: api.ExecutionEvent) => {
    switch (event.type) {
      case 'thinking':
        updateLastMessage({ content: `🤔 ${event.message}` })
        break
        
      case 'planning':
        updateLastMessage({ content: `📋 ${event.message}` })
        break
        
      case 'step_start':
        if (event.step !== undefined) {
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
        }
        break
        
      case 'step_complete':
        if (event.step !== undefined) {
          setCurrentPlan((prev) => {
            if (!prev) return prev
            const updated = [...prev]
            const idx = event.step! - 1
            if (updated[idx]) {
              updated[idx] = { ...updated[idx], status: 'completed' }
            }
            return updated
          })
          if (event.file && event.content) {
            onFileCreated?.(event.file, event.content, event.language || 'text')
          }
        }
        break
        
      case 'step_error':
        if (event.step !== undefined) {
          setCurrentPlan((prev) => {
            if (!prev) return prev
            const updated = [...prev]
            const idx = event.step! - 1
            if (updated[idx]) {
              updated[idx] = { ...updated[idx], status: 'failed' }
            }
            return updated
          })
        }
        break
        
      case 'complete':
        setIsExecuting(false)
        addMessage({
          role: 'assistant',
          content: `✅ Project complete! ${event.total_files || event.files_created?.length || 0} files created.\n\nYour project is ready! You can:\n• Browse the code in the file explorer\n• Preview the application\n• Download or publish your project`,
          type: 'complete',
        })
        onExecutionComplete?.(event.files_created || [])
        break
        
      case 'error':
        setIsExecuting(false)
        addMessage({
          role: 'system',
          content: `❌ Error: ${event.message || event.error}`,
          type: 'error',
        })
        break
    }
  }

  // REMOVED: runLocalExecution function - no more demo mode
  // All code generation now requires real OpenAI API connection

  const cancelExecution = () => {
    if (cleanupRef.current) {
      cleanupRef.current()
      cleanupRef.current = null
    }
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
    setCurrentPlan(null)
    setCurrentProjectId(null)
    setCurrentExecutionId(null)
    addMessage({ role: 'user', content: userMessage })
    await analyzeAndPlan(userMessage)
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-border">
      <div className="h-14 border-b border-border px-4 flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-sm">AI Builder</h2>
          <p className="text-xs text-secondary">
            {isExecuting ? 'Building...' : isThinking ? 'Thinking...' : 'Ready to build'}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center mx-auto mb-4">
              <Bot className="w-8 h-8 text-secondary" />
            </div>
            <h3 className="font-semibold mb-2">AI Builder</h3>
            <p className="text-secondary text-sm max-w-xs mx-auto">
              Describe what you want to build and I&apos;ll create it step by step with real files.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${message.role === 'user' ? 'bg-primary' : 'bg-surface'}`}>
              {message.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`flex-1 ${message.role === 'user' ? 'text-right' : ''}`}>
              <div className={`inline-block rounded-xl px-4 py-3 max-w-[90%] ${message.role === 'user' ? 'bg-primary text-white' : 'bg-surface'}`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                {message.plan && (
                  <div className="mt-4 space-y-2">
                    {message.plan.map((step) => (
                      <div key={step.id} className="flex items-center gap-2 text-sm text-secondary">
                        {step.status === 'completed' ? (
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                        ) : step.status === 'executing' ? (
                          <Loader2 className="w-4 h-4 animate-spin text-accent flex-shrink-0" />
                        ) : step.status === 'failed' ? (
                          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border-2 border-current flex-shrink-0" />
                        )}
                        <span className="flex-1">{step.id}. {step.description}</span>
                        {step.file_path && <FileCode className="w-3 h-3 text-muted" />}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <p className="text-xs text-muted mt-1">{message.timestamp.toLocaleTimeString()}</p>
            </div>
          </div>
        ))}

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

      <form onSubmit={handleSubmit} className="p-4 border-t border-border">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe what you want to build..."
            className="input flex-1"
            disabled={isThinking || isExecuting || awaitingConfirmation}
          />
          <Button type="submit" disabled={!input.trim() || isThinking || isExecuting || awaitingConfirmation}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}
