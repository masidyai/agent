'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Layers, Server, RefreshCw, ShoppingCart, MessageSquare, Calendar } from 'lucide-react'
import { Card, CardContent, Button } from '@/components/ui'

const examples = [
  {
    icon: Layers,
    title: 'Task Management SaaS',
    description: 'Full-stack app with user auth, CRUD tasks, and a modern dashboard',
    prompt: 'Build a task management SaaS with user authentication and a modern dashboard',
    flow: 'saas',
    tags: ['FastAPI', 'React', 'Auth', 'Docker'],
  },
  {
    icon: Server,
    title: 'REST API Service',
    description: 'Production-ready API with endpoints, database, tests, and CI/CD',
    prompt: 'Create a REST API for a notes application with full CRUD operations',
    flow: 'api',
    tags: ['FastAPI', 'SQLite', 'pytest', 'Docker'],
  },
  {
    icon: RefreshCw,
    title: 'Modernize Repository',
    description: 'Add Docker, CI/CD, tests, and documentation to any existing project',
    prompt: 'Modernize this repository and add CI/CD pipeline',
    flow: 'refactor',
    tags: ['Docker', 'GitHub Actions', 'Testing'],
  },
  {
    icon: ShoppingCart,
    title: 'E-commerce Backend',
    description: 'Complete backend with products, orders, payments integration',
    prompt: 'Build an e-commerce backend API with products, orders, and Stripe integration',
    flow: 'api',
    tags: ['FastAPI', 'PostgreSQL', 'Stripe'],
  },
  {
    icon: MessageSquare,
    title: 'Chat Application',
    description: 'Real-time chat with rooms, messages, and user presence',
    prompt: 'Build a real-time chat application with WebSocket support',
    flow: 'saas',
    tags: ['FastAPI', 'WebSocket', 'React'],
  },
  {
    icon: Calendar,
    title: 'Booking System',
    description: 'Appointment scheduling with calendar, notifications, and admin panel',
    prompt: 'Create a booking and appointment scheduling system',
    flow: 'saas',
    tags: ['FastAPI', 'React', 'Email'],
  },
]

export function Examples() {
  const router = useRouter()

  const handleTryExample = (prompt: string) => {
    router.push(`/ide?prompt=${encodeURIComponent(prompt)}`)
  }

  return (
    <section id="examples" className="section bg-white">
      <div className="container-custom px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="heading-2 mb-4">Rich ready-made examples</h2>
          <p className="text-body max-w-2xl mx-auto">
            Get started instantly with these production-ready templates. 
            Each example is fully functional and deployable in minutes.
          </p>
        </div>

        {/* Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {examples.map((example) => (
            <Card key={example.title} className="group">
              <CardContent>
                <div className="w-12 h-12 bg-surface rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-white transition-colors">
                  <example.icon className="w-6 h-6" />
                </div>
                <h3 className="heading-3 mb-2">{example.title}</h3>
                <p className="text-secondary mb-4">{example.description}</p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {example.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-surface rounded text-xs font-medium text-secondary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Action */}
                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-colors"
                  onClick={() => handleTryExample(example.prompt)}
                >
                  Try this example
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
