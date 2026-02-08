'use client'

import React from 'react'
import { 
  Layers, Zap, Code2, GitBranch, Shield, Repeat, 
  Database, Cloud, Terminal, FileCode, Bot, Puzzle 
} from 'lucide-react'

const features = [
  {
    icon: Layers,
    title: 'Three Powerful Flows',
    description: 'SaaS apps, API services, or repository refactoring — choose your flow and let Masidy handle the rest.',
  },
  {
    icon: Zap,
    title: 'Instant Execution',
    description: 'From prompt to production-ready code in minutes. No waiting, no manual setup.',
  },
  {
    icon: Code2,
    title: 'Full-Stack Generation',
    description: 'Backend, frontend, database, auth, Docker, CI/CD — everything you need, generated automatically.',
  },
  {
    icon: GitBranch,
    title: 'GitHub Integration',
    description: 'Connect your repositories, push code, create PRs — all from within Masidy.',
  },
  {
    icon: Shield,
    title: 'Production Ready',
    description: 'Every generated project includes tests, proper error handling, and security best practices.',
  },
  {
    icon: Repeat,
    title: 'Smart Retries',
    description: 'Automatic retry logic ensures every step completes successfully, even with transient failures.',
  },
  {
    icon: Database,
    title: 'Database Support',
    description: 'SQLite for simplicity or PostgreSQL for scale — database layer included and configured.',
  },
  {
    icon: Cloud,
    title: 'Docker Ready',
    description: 'Dockerfile and docker-compose included. Deploy anywhere with a single command.',
  },
  {
    icon: Terminal,
    title: '33+ Built-in Tools',
    description: 'File operations, shell commands, git actions — powerful tools at your AI agent\'s disposal.',
  },
  {
    icon: FileCode,
    title: 'Clean Code',
    description: 'Well-structured, maintainable code following best practices and modern patterns.',
  },
  {
    icon: Bot,
    title: 'AI Planning',
    description: 'Intelligent planning with structured steps, so you always know what\'s happening.',
  },
  {
    icon: Puzzle,
    title: 'Extensible',
    description: 'Add custom tools, flows, and integrations. Masidy grows with your needs.',
  },
]

export function Features() {
  return (
    <section id="features" className="section bg-surface">
      <div className="container-custom px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="heading-2 mb-4">Showcase of Masidy features</h2>
          <p className="text-body max-w-2xl mx-auto">
            Everything you need to build complete applications, powered by 
            intelligent AI agents and a comprehensive toolset.
          </p>
        </div>

        {/* Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="bg-white rounded-xl p-6 border border-border hover:shadow-md transition-shadow"
            >
              <div className="w-10 h-10 bg-surface rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-secondary text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
