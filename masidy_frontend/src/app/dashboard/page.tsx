'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Project {
  id: string
  name: string
  description: string
  project_type: string
  status: string
  created_at: string
  runs?: Run[]
}

interface Run {
  id: string
  status: string
  steps_completed: number
  steps_total: number
}

const quickActions = [
  {
    icon: '📦',
    title: 'Build a SaaS App',
    description: 'Full-stack with auth, database, and UI',
    template: 'saas',
    prompt: 'Build a SaaS application with user authentication, dashboard, and billing',
  },
  {
    icon: '🔌',
    title: 'Create an API',
    description: 'REST API with CRUD, tests, and docs',
    template: 'api',
    prompt: 'Create a REST API service with CRUD operations, authentication, and documentation',
  },
  {
    icon: '🔄',
    title: 'Refactor a Repo',
    description: 'Add Docker, CI/CD, and modernize',
    template: 'refactor',
    prompt: 'Modernize this repository with Docker, CI/CD pipeline, and best practices',
  },
]

export default function DashboardPage() {
  const router = useRouter()
  const [prompt, setPrompt] = useState('')
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setProjects(data)
      } else if (response.status === 401) {
        router.push('/login')
      }
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const createProject = async (name: string, description: string, template?: string) => {
    setCreating(true)
    setError('')
    
    try {
      const token = localStorage.getItem('access_token')
      
      // Create project
      const projectRes = await fetch(`${API_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.toLowerCase().replace(/\s+/g, '_'),
          description,
          project_type: template || 'custom',
        }),
      })

      if (!projectRes.ok) {
        throw new Error('Failed to create project')
      }

      const project = await projectRes.json()

      // Create run for the project
      const runRes = await fetch(`${API_URL}/api/projects/${project.id}/runs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: description,
        }),
      })

      if (!runRes.ok) {
        throw new Error('Failed to create run')
      }

      const run = await runRes.json()

      // Redirect to IDE with the run
      router.push(`/runs/${run.id}`)
    } catch (err) {
      setError('Failed to create project. Please try again.')
      console.error(err)
    } finally {
      setCreating(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      const projectName = prompt.split(' ').slice(0, 3).join('_').toLowerCase()
      createProject(projectName, prompt)
    }
  }

  const handleQuickAction = (action: typeof quickActions[0]) => {
    createProject(action.title.toLowerCase().replace(/\s+/g, '_'), action.prompt, action.template)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-yellow-100 text-yellow-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Welcome back!</h1>
        <p className="text-gray-600">What would you like to build today?</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Create Project Form */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <label className="block text-sm font-medium mb-2">
            Describe your project
          </label>
          <div className="flex gap-4">
            <input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Build a task management app with user authentication..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              disabled={creating}
            />
            <button 
              type="submit" 
              disabled={creating || !prompt.trim()}
              className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {creating ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Creating...
                </>
              ) : (
                <>
                  <span>+</span>
                  Create
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Quick Start */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Quick Start</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.title}
              onClick={() => handleQuickAction(action)}
              disabled={creating}
              className="bg-white border border-gray-200 rounded-xl p-6 text-left hover:border-black transition group disabled:opacity-50"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{action.icon}</div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1 flex items-center gap-2">
                    {action.title}
                    <span className="text-gray-400 group-hover:translate-x-1 transition-transform">→</span>
                  </h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Recent Projects</h2>
          <Link href="/dashboard/projects" className="text-sm text-gray-600 hover:text-black">
            View all
          </Link>
        </div>
        
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-xl p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-4" />
                <div className="h-6 bg-gray-200 rounded w-1/4" />
              </div>
            ))}
          </div>
        ) : projects.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.slice(0, 6).map((project) => (
              <div key={project.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 transition">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">
                      {project.project_type === 'saas' ? '📦' : project.project_type === 'api' ? '🔌' : '📁'}
                    </span>
                    <h3 className="font-semibold">{project.name}</h3>
                  </div>
                  <button className="text-gray-400 hover:text-gray-600">⋮</button>
                </div>
                <p className="text-sm text-gray-500 mb-3 capitalize">{project.project_type}</p>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(project.status)}`}>
                    {project.status === 'in_progress' ? 'In Progress' : project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                  </span>
                  <span className="text-xs text-gray-500">{formatDate(project.created_at)}</span>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                  <Link 
                    href={`/runs/${project.runs?.[0]?.id || project.id}`}
                    className="text-sm font-medium text-black hover:underline flex items-center gap-1"
                  >
                    Open <span>↗</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="text-5xl mb-4">📁</div>
            <h3 className="font-semibold mb-2">No projects yet</h3>
            <p className="text-gray-500 mb-4">Start building your first project</p>
            <button 
              onClick={() => document.querySelector('input')?.focus()}
              className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
            >
              Create your first project
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
