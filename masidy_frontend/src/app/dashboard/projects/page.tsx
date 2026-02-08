'use client'

import { useState, useEffect } from 'react'
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
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

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

  const deleteProject = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return

    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${API_URL}/api/projects/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      setProjects(projects.filter(p => p.id !== id))
    } catch (err) {
      console.error('Failed to delete project:', err)
    }
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

  const filteredProjects = projects.filter(project => {
    const matchesFilter = filter === 'all' || project.status === filter
    const matchesSearch = project.name.toLowerCase().includes(search.toLowerCase()) ||
                         project.description?.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Projects</h1>
          <p className="text-gray-600">Manage all your projects in one place.</p>
        </div>
        <Link
          href="/dashboard/new-project"
          className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
        >
          + New Project
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search projects..."
          className="flex-1 max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="in_progress">In Progress</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Projects List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-xl p-6 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 bg-gray-200 rounded-lg" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredProjects.length > 0 ? (
        <div className="space-y-4">
          {filteredProjects.map((project) => (
            <div key={project.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:border-gray-300 transition">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">
                    {project.project_type === 'saas' ? '📦' : project.project_type === 'api' ? '🔌' : '📁'}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{project.name}</h3>
                    <p className="text-gray-500 text-sm">{project.description || 'No description'}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 text-sm font-medium rounded ${getStatusColor(project.status)}`}>
                    {project.status === 'in_progress' ? 'In Progress' : project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                  </span>
                  <span className="text-sm text-gray-500">{formatDate(project.created_at)}</span>
                  
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/runs/${project.id}`}
                      className="px-4 py-2 bg-black text-white rounded-lg text-sm hover:bg-gray-800 transition"
                    >
                      Open
                    </Link>
                    <button
                      onClick={() => deleteProject(project.id)}
                      className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition text-red-600"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="text-5xl mb-4">📁</div>
          <h3 className="font-semibold mb-2">No projects found</h3>
          <p className="text-gray-500 mb-4">
            {search || filter !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Create your first project to get started'}
          </p>
          <Link
            href="/dashboard/new-project"
            className="inline-block px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
          >
            Create Project
          </Link>
        </div>
      )}
    </div>
  )
}
