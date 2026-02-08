/**
 * Masidy API Client - Production Ready
 * 
 * Connects the frontend to the backend API for project execution.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============================================================================
// Types
// ============================================================================

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
  files: string[]
}

export interface PlanStep {
  id: number
  description: string
  tool_name: string
  status: string
  file_path?: string
}

export interface ExecutionPlan {
  project_id: string
  flow: string
  steps: PlanStep[]
  estimated_time: string
  total_files: number
}

export interface Flow {
  id: string
  name: string
  description: string
  steps: number
}

export interface FileContent {
  path: string
  content: string
  language: string
}

export interface ExecutionEvent {
  type: 'thinking' | 'planning' | 'step_start' | 'step_complete' | 'step_error' | 'complete' | 'error'
  step?: number
  total?: number
  description?: string
  message?: string
  file?: string
  content?: string
  language?: string
  files_created?: string[]
  total_files?: number
  error?: string
}

export interface PlanAndExecuteResult {
  project_id: string
  execution_id: string
  name: string
  steps_total: number
}

// ============================================================================
// API Functions
// ============================================================================

export async function healthCheck(): Promise<{ status: string; projects_count: number }> {
  const response = await fetch(`${API_BASE}/api/health`)
  if (!response.ok) throw new Error('Health check failed')
  return response.json()
}

export async function listProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/api/projects`)
  if (!response.ok) throw new Error('Failed to list projects')
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
  if (!response.ok) throw new Error('Failed to create project')
  return response.json()
}

export async function getProject(projectId: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}`)
  if (!response.ok) throw new Error('Project not found')
  return response.json()
}

export async function deleteProject(projectId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete project')
}

export async function generatePlan(prompt: string, flow: string = 'saas'): Promise<ExecutionPlan> {
  const response = await fetch(`${API_BASE}/api/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, flow }),
  })
  if (!response.ok) throw new Error('Failed to generate plan')
  return response.json()
}

export async function getExecutionPlan(projectId: string): Promise<ExecutionPlan> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/plan`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to get execution plan')
  return response.json()
}

export async function startExecution(projectId: string): Promise<{ execution_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/execute`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to start execution')
  return response.json()
}

export async function planAndExecute(prompt: string, flow: string = 'saas'): Promise<PlanAndExecuteResult> {
  const response = await fetch(`${API_BASE}/api/plan-and-execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, flow }),
  })
  if (!response.ok) throw new Error('Failed to plan and execute')
  return response.json()
}

export function streamExecution(
  executionId: string,
  onMessage: (data: ExecutionEvent) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): () => void {
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
      console.error('Failed to parse SSE event:', e)
    }
  }

  eventSource.onerror = () => {
    eventSource.close()
    onError?.(new Error('Connection lost'))
  }

  // Return cleanup function
  return () => eventSource.close()
}

export async function getProjectFiles(projectId: string): Promise<{ files: Array<{ path: string; size: number }> }> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/files`)
  if (!response.ok) throw new Error('Failed to get project files')
  return response.json()
}

export async function getFileContent(projectId: string, filePath: string): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/files/${encodeURIComponent(filePath)}`)
  if (!response.ok) throw new Error('Failed to get file content')
  return response.json()
}

export async function listFlows(): Promise<{ flows: Flow[] }> {
  const response = await fetch(`${API_BASE}/api/flows`)
  if (!response.ok) throw new Error('Failed to list flows')
  return response.json()
}

export async function listTools(): Promise<{ tools: Array<{ name: string; description: string }>; total: number }> {
  const response = await fetch(`${API_BASE}/api/tools`)
  if (!response.ok) throw new Error('Failed to list tools')
  return response.json()
}
