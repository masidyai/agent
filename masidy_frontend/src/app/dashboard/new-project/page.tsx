'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const templates = [
  {
    id: 'saas',
    name: 'SaaS Application',
    description: 'Full-stack app with authentication, dashboard, and billing',
    icon: '📦',
  },
  {
    id: 'api',
    name: 'REST API',
    description: 'Backend API with CRUD operations and documentation',
    icon: '🔌',
  },
  {
    id: 'refactor',
    name: 'Refactor Project',
    description: 'Add Docker, CI/CD, and modernize existing code',
    icon: '🔧',
  },
]

export default function NewProjectPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  
  const [project, setProject] = useState({
    name: '',
    description: '',
    template: 'saas',
  })

  const handleCreate = async () => {
    if (!project.name.trim()) {
      setError('Project name is required')
      return
    }

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
          name: project.name.toLowerCase().replace(/\s+/g, '_'),
          prompt: project.description || `Create a ${project.template} project`,
          flow: project.template,
        }),
      })

      if (!projectRes.ok) {
        throw new Error('Failed to create project')
      }

      const createdProject = await projectRes.json()

      // Create initial run
      const runRes = await fetch(`${API_URL}/api/projects/${createdProject.id}/runs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: project.description || `Create a ${project.template} project`,
        }),
      })

      if (runRes.ok) {
        const run = await runRes.json()
        router.push(`/runs/${run.id}`)
      } else {
        router.push(`/dashboard/projects`)
      }
    } catch (err) {
      setError('Failed to create project. Please try again.')
      console.error(err)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Create New Project</h1>
      <p className="text-gray-600 mb-8">Set up a new project in just a few steps.</p>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Progress Steps */}
      <div className="flex items-center mb-8">
        {[1, 2].map((s) => (
          <div key={s} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
              step >= s ? 'bg-black text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              {s}
            </div>
            <span className={`ml-2 ${step >= s ? 'font-medium' : 'text-gray-500'}`}>
              {s === 1 ? 'Choose Template' : 'Project Details'}
            </span>
            {s < 2 && <div className="w-16 h-0.5 bg-gray-200 mx-4" />}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Choose a template</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <button
                key={template.id}
                onClick={() => {
                  setProject({ ...project, template: template.id })
                  setStep(2)
                }}
                className={`p-6 border rounded-xl text-left transition ${
                  project.template === template.id
                    ? 'border-black bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-3xl mb-3">{template.icon}</div>
                <h3 className="font-semibold mb-1">{template.name}</h3>
                <p className="text-sm text-gray-600">{template.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Project Details</h2>
          
          <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Project Name *</label>
              <input
                type="text"
                value={project.name}
                onChange={(e) => setProject({ ...project, name: e.target.value })}
                placeholder="my-awesome-project"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-sm text-gray-500 mt-1">
                This will be used as the repository name
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={project.description}
                onChange={(e) => setProject({ ...project, description: e.target.value })}
                placeholder="Describe what you want to build..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black resize-none"
              />
              <p className="text-sm text-gray-500 mt-1">
                Be specific about features, tech stack, and requirements
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Template:</span> {templates.find(t => t.id === project.template)?.name}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 mt-6">
            <button
              onClick={() => setStep(1)}
              className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition"
            >
              Back
            </button>
            <button
              onClick={handleCreate}
              disabled={creating || !project.name.trim()}
              className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50 flex items-center gap-2"
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
                'Create Project'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
