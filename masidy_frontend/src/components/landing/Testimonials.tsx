'use client'

import React from 'react'
import { Star } from 'lucide-react'

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Startup Founder',
    avatar: 'SC',
    content: 'Masidy helped us launch our MVP in 2 days instead of 2 months. The generated code is clean and production-ready.',
    rating: 5,
  },
  {
    name: 'Marcus Johnson',
    role: 'Senior Developer',
    avatar: 'MJ',
    content: 'I use Masidy to scaffold new projects. It sets up everything perfectly - Docker, CI/CD, tests. Saves hours of boilerplate work.',
    rating: 5,
  },
  {
    name: 'Elena Rodriguez',
    role: 'Tech Lead',
    avatar: 'ER',
    content: 'The refactor flow is amazing. We modernized our legacy codebase in a fraction of the time it would have taken manually.',
    rating: 5,
  },
  {
    name: 'David Kim',
    role: 'Indie Hacker',
    avatar: 'DK',
    content: 'As a solo developer, Masidy is like having a whole team. I can focus on features while it handles the infrastructure.',
    rating: 5,
  },
  {
    name: 'Lisa Thompson',
    role: 'Product Manager',
    avatar: 'LT',
    content: 'Even non-developers on our team can prototype ideas. Masidy bridges the gap between vision and implementation.',
    rating: 5,
  },
  {
    name: 'Alex Petrov',
    role: 'DevOps Engineer',
    avatar: 'AP',
    content: 'The Docker and CI/CD setup is exactly what I would configure manually. Masidy gets the details right.',
    rating: 5,
  },
]

export function Testimonials() {
  return (
    <section className="section bg-surface">
      <div className="container-custom px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="heading-2 mb-4">Loved by developers worldwide</h2>
          <p className="text-body max-w-2xl mx-auto">
            Join thousands of developers who build faster with Masidy.
          </p>
        </div>

        {/* Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.name}
              className="bg-white rounded-xl p-6 border border-border"
            >
              {/* Stars */}
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>

              {/* Content */}
              <p className="text-secondary mb-6">&quot;{testimonial.content}&quot;</p>

              {/* Author */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-sm text-secondary">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
