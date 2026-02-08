'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Upload, Github, Zap, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui'

export function Hero() {
  const [prompt, setPrompt] = useState('')
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      router.push(`/ide?prompt=${encodeURIComponent(prompt)}`)
    }
  }

  const quickPrompts = [
    'Build a task management SaaS',
    'Create a REST API for notes',
    'Build a blog platform',
  ]

  return (
    <section className="section pt-32 pb-20 bg-gradient-to-b from-surface to-white">
      <div className="container-custom text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-white border border-border rounded-full px-4 py-2 mb-8 shadow-sm">
          <Sparkles className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium">AI-Powered Development Platform</span>
        </div>

        {/* Headline */}
        <h1 className="heading-1 max-w-4xl mx-auto mb-6">
          What do you want to{' '}
          <span className="bg-gradient-to-r from-accent to-purple-600 text-transparent bg-clip-text">
            build today
          </span>{' '}
          with Masidy?
        </h1>

        {/* Subheadline */}
        <p className="text-body max-w-2xl mx-auto mb-12">
          Masidy is the all-in-one AI agent platform that builds complete, production-ready 
          applications from a simple prompt. SaaS apps, APIs, and more — in minutes.
        </p>

        {/* Main Input */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto mb-8">
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to build... e.g. 'Build a task management SaaS with user auth'"
              className="input input-lg pr-32 min-h-[120px] resize-none text-lg"
              rows={3}
            />
            <div className="absolute bottom-4 right-4 flex items-center gap-2">
              <Button type="submit" size="lg" className="gap-2">
                Start Building
                <ArrowRight className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap justify-center gap-3 mt-4">
            <button
              type="button"
              className="flex items-center gap-2 text-secondary hover:text-primary transition-colors text-sm"
            >
              <Upload className="w-4 h-4" />
              Upload files
            </button>
            <span className="text-border">|</span>
            <button
              type="button"
              className="flex items-center gap-2 text-secondary hover:text-primary transition-colors text-sm"
            >
              <Github className="w-4 h-4" />
              Connect GitHub
            </button>
            <span className="text-border">|</span>
            <button
              type="button"
              className="flex items-center gap-2 text-secondary hover:text-primary transition-colors text-sm"
            >
              <Zap className="w-4 h-4" />
              Quick start
            </button>
          </div>
        </form>

        {/* Quick Prompts */}
        <div className="flex flex-wrap justify-center gap-3">
          {quickPrompts.map((quickPrompt) => (
            <button
              key={quickPrompt}
              onClick={() => setPrompt(quickPrompt)}
              className="px-4 py-2 bg-white border border-border rounded-full text-sm text-secondary hover:text-primary hover:border-primary transition-all"
            >
              {quickPrompt}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto mt-16 pt-16 border-t border-border">
          <div>
            <div className="text-3xl font-bold">10k+</div>
            <div className="text-secondary text-sm">Projects Built</div>
          </div>
          <div>
            <div className="text-3xl font-bold">33+</div>
            <div className="text-secondary text-sm">Built-in Tools</div>
          </div>
          <div>
            <div className="text-3xl font-bold">3</div>
            <div className="text-secondary text-sm">Flow Types</div>
          </div>
        </div>
      </div>
    </section>
  )
}
