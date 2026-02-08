'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { DashboardSidebar, ProjectCard } from '@/components/dashboard'
import { Button, Card, CardContent } from '@/components/ui'
import { Plus, Layers, Server, RefreshCw, ArrowRight } from 'lucide-react'

const quickActions = [
  {
    icon: Layers,
    title: 'Build a SaaS App',
    description: 'Full-stack with auth, database, and UI',
    flow: 'saas',
    prompt: 'Build a SaaS application',
  },
  {
    icon: Server,
    title: 'Create an API',
    description: 'REST API with CRUD, tests, and docs',
    flow: 'api',
    prompt: 'Create a REST API service',
  },
  {
    icon: RefreshCw,
    title: 'Refactor a Repo',
    description: 'Add Docker, CI/CD, and modernize',
    flow: 'refactor',
    prompt: 'Modernize this repository',
  },
]

const mockProjects = [
  {
    id: '1',
    name: 'task_manager',
    type: 'saas' as const,
    status: 'completed' as const,
    createdAt: '2024-02-08T10:00:00Z',
    stepsCompleted: 45,
    stepsTotal: 45,
  },
  {
    id: '2',
    name: 'notes_api',
    type: 'api' as const,
    status: 'completed' as const,
    createdAt: '2024-02-07T14:00:00Z',
    stepsCompleted: 33,
    stepsTotal: 33,
  },
  {
    id: '3',
    name: 'legacy_project',
    type: 'refactor' as const,
    status: 'in_progress' as const,
    createdAt: '2024-02-08T11:00:00Z',
    stepsCompleted: 8,
    stepsTotal: 12,
  },
]

export default function DashboardPage() {
  const router = useRouter()
  const [prompt, setPrompt] = useState('')
  const projects = mockProjects

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      router.push(`/ide?prompt=${encodeURIComponent(prompt)}`)
    }
  }

  const handleQuickAction = (action: typeof quickActions[0]) => {
    router.push(`/ide?prompt=${encodeURIComponent(action.prompt)}&flow=${action.flow}`)
  }

  return (
    <div className="flex min-h-screen bg-surface">
      <DashboardSidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="heading-2 mb-2">Welcome back!</h1>
          <p className="text-secondary">What would you like to build today?</p>
        </div>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="bg-white rounded-xl border border-border p-6">
            <label className="block text-sm font-medium mb-2">
              Describe your project
            </label>
            <div className="flex gap-4">
              <input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Build a task management app with user authentication..."
                className="input flex-1"
              />
              <Button type="submit" className="gap-2">
                <Plus className="w-4 h-4" />
                Create
              </Button>
            </div>
          </div>
        </form>

        <div className="mb-8">
          <h2 className="heading-3 mb-4">Quick Start</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Card
                key={action.title}
                className="cursor-pointer group"
                onClick={() => handleQuickAction(action)}
              >
                <CardContent>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-surface rounded-xl flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-colors">
                      <action.icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">{action.title}</h3>
                      <p className="text-sm text-secondary">{action.description}</p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-secondary group-hover:text-primary transition-colors" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-3">Recent Projects</h2>
            <Button variant="ghost" size="sm">View all</Button>
          </div>
          
          {projects.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project) => (
                <ProjectCard key={project.id} {...project} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-border p-12 text-center">
              <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center mx-auto mb-4">
                <Layers className="w-8 h-8 text-secondary" />
              </div>
              <h3 className="font-semibold mb-2">No projects yet</h3>
              <p className="text-secondary mb-4">Start building your first project</p>
              <Button onClick={() => router.push('/ide')}>Create your first project</Button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
