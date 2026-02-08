'use client'

import React, { useState } from 'react'
import { Button, Input } from '@/components/ui'
import { ArrowRight, CheckCircle } from 'lucide-react'

export function Newsletter() {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) {
      setSubscribed(true)
      setEmail('')
    }
  }

  return (
    <section className="section bg-primary text-white">
      <div className="container-custom px-4 text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Stay updated with Masidy
        </h2>
        <p className="text-white/80 max-w-xl mx-auto mb-8">
          Get the latest updates, new features, and tips delivered to your inbox. 
          No spam, unsubscribe anytime.
        </p>

        {subscribed ? (
          <div className="flex items-center justify-center gap-2 text-green-400">
            <CheckCircle className="w-5 h-5" />
            <span>Thanks for subscribing! Check your inbox.</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 rounded-lg text-primary"
              required
            />
            <Button
              type="submit"
              variant="secondary"
              className="bg-white text-primary hover:bg-gray-100"
            >
              Subscribe
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </form>
        )}
      </div>
    </section>
  )
}
