/**
 * Masidy API Client
 * 
 * Connects the frontend to the backend API for project execution.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Project {
  id: string
  name: string
  prompt: string
  flow: string
  status: string
  created_at: string
  steps_completed: number
  steps_total: number
  output_path?: string
}

export interface PlanStep {
  id: number
  description: string
  tool_name: string
  status: string
}

export interface ExecutionPlan {
  project_id: string
  flow: string
  steps: PlanStep[]
  estimated_time: string
}

export interface Flow {
  id: string
  name: string
  description: string
  steps: number
}

// API Functions

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/api/health`)
  return response.json()
}

export async function listProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/api/projects`)
  return response.json()
}

export async function createProject(
  prompt: string,
  flow: string = 'saas',
  name?: string
): Promise<Project> {
  const response = await fetch(`${API_BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, flow, name }),
  })
  return response.json()
}

export async function getProject(projectId: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}`)
  return response.json()
}

export async function getExecutionPlan(projectId: string): Promise<ExecutionPlan> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/plan`, {
    method: 'POST',
  })
  return response.json()
}

export async function startExecution(
  projectId: string
): Promise<{ execution_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/execute`, {
    method: 'POST',
  })
  return response.json()
}

export async function streamExecution(
  executionId: string,
  onMessage: (data: ExecutionEvent) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): Promise<void> {
  const eventSource = new EventSource(`${API_BASE}/api/executions/${executionId}/stream`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as ExecutionEvent
      onMessage(data)
      
      if (data.type === 'complete' || data.type === 'error') {
        eventSource.close()
        onComplete?.()
      }
    } catch (e) {
      console.error('Failed to parse event:', e)
    }
  }

  eventSource.onerror = (error) => {
    console.error('EventSource error:', error)
    eventSource.close()
    onError?.(new Error('Connection lost'))
  }
}

export interface ExecutionEvent {
  type: 'step_start' | 'step_complete' | 'file_created' | 'complete' | 'error'
  step?: number
  total?: number
  description?: string
  file?: string
  files_created?: string[]
  error?: string
}

export async function listFlows(): Promise<{ flows: Flow[] }> {
  const response = await fetch(`${API_BASE}/api/flows`)
  return response.json()
}

export async function listTools(): Promise<{ tools: { name: string; description: string }[]; total: number }> {
  const response = await fetch(`${API_BASE}/api/tools`)
  return response.json()
}
