/**
 * Masidy API Client - Production Ready
 * 
 * Connects the frontend to the backend API for project execution.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper to get auth headers
const getAuthHeaders = (): HeadersInit => {
  if (typeof window === 'undefined') return {}
  const tokens = localStorage.getItem('auth_tokens')
  if (!tokens) return {}
  const { access_token } = JSON.parse(tokens)
  return { Authorization: `Bearer ${access_token}` }
}

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

// ============================================================================
// New v1 API Functions
// ============================================================================

export interface User {
  id: string
  email: string
  name: string | null
  avatar_url: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Team {
  id: string
  name: string
  description?: string
  owner_id: string
  created_at: string
}

export interface BillingPlan {
  projects: number
  executions: number
  deployments: number
  team_members: number
  price_monthly: number
  price_yearly: number
  features: string[]
}

export interface Deployment {
  id: string
  project_id: string
  environment: string
  status: string
  provider: string
  url?: string
  preview_url?: string
  created_at: string
}

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/api/v1/auth/login/json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) throw new Error('Login failed')
    return res.json()
  },

  register: async (email: string, password: string, name: string) => {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    })
    if (!res.ok) throw new Error('Registration failed')
    return res.json()
  },

  me: async (): Promise<User> => {
    const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error('Not authenticated')
    return res.json()
  },

  refresh: async (refreshToken: string) => {
    const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!res.ok) throw new Error('Token refresh failed')
    return res.json()
  },
}

// Projects v1 API
export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const res = await fetch(`${API_BASE}/api/v1/projects/`, {
      headers: getAuthHeaders(),
    })
    return res.json()
  },

  get: async (id: string): Promise<Project> => {
    const res = await fetch(`${API_BASE}/api/v1/projects/${id}`, {
      headers: getAuthHeaders(),
    })
    return res.json()
  },

  create: async (data: { name: string; description?: string; prompt?: string; flow?: string }): Promise<Project> => {
    const res = await fetch(`${API_BASE}/api/v1/projects/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    })
    return res.json()
  },

  delete: async (id: string): Promise<void> => {
    await fetch(`${API_BASE}/api/v1/projects/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })
  },
}

// Teams API
export const teamsApi = {
  list: async (): Promise<Team[]> => {
    const res = await fetch(`${API_BASE}/api/v1/teams/`, {
      headers: getAuthHeaders(),
    })
    return res.json()
  },

  create: async (data: { name: string; description?: string }): Promise<Team> => {
    const res = await fetch(`${API_BASE}/api/v1/teams/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    })
    return res.json()
  },

  invite: async (teamId: string, email: string, role: string = 'member') => {
    const res = await fetch(`${API_BASE}/api/v1/teams/${teamId}/invite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ email, role }),
    })
    return res.json()
  },
}

// Billing API
export const billingApi = {
  getPlans: async (): Promise<{ plans: Record<string, BillingPlan> }> => {
    const res = await fetch(`${API_BASE}/api/v1/billing/plans`)
    return res.json()
  },

  getCurrent: async () => {
    const res = await fetch(`${API_BASE}/api/v1/billing/`, {
      headers: getAuthHeaders(),
    })
    return res.json()
  },

  upgrade: async (plan: string) => {
    const res = await fetch(`${API_BASE}/api/v1/billing/upgrade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ plan }),
    })
    return res.json()
  },
}

// Deployments API
export const deploymentsApi = {
  list: async (projectId: string): Promise<Deployment[]> => {
    const res = await fetch(`${API_BASE}/api/v1/deployments/?project_id=${projectId}`, {
      headers: getAuthHeaders(),
    })
    return res.json()
  },

  create: async (projectId: string, provider: string = 'vercel', environment: string = 'production') => {
    const res = await fetch(`${API_BASE}/api/v1/deployments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ project_id: projectId, provider, environment }),
    })
    return res.json()
  },
}

// Visual Builder API
export const visualBuilderApi = {
  getComponents: async () => {
    const res = await fetch(`${API_BASE}/api/v1/visual-builder/components`)
    return res.json()
  },

  getTemplates: async () => {
    const res = await fetch(`${API_BASE}/api/v1/visual-builder/templates`)
    return res.json()
  },

  createPage: async (data: { name: string; path: string; template?: string }) => {
    const res = await fetch(`${API_BASE}/api/v1/visual-builder/pages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    })
    return res.json()
  },
}

// Sandbox API
export const sandboxApi = {
  execute: async (command: string, timeout: number = 30) => {
    const res = await fetch(`${API_BASE}/api/v1/sandbox/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ command, timeout }),
    })
    return res.json()
  },

  executeCode: async (code: string, language: string) => {
    const res = await fetch(`${API_BASE}/api/v1/sandbox/execute-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ code, language }),
    })
    return res.json()
  },
}
