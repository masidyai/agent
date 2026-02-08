'use client'

import React from 'react'
import { Check } from 'lucide-react'
import { Button } from '@/components/ui'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for trying out Masidy',
    features: [
      '3 projects per month',
      'API flow only',
      'Basic support',
      'Community access',
    ],
    cta: 'Get Started',
    popular: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: 'per month',
    description: 'For individual developers',
    features: [
      'Unlimited projects',
      'All flows (SaaS, API, Refactor)',
      'Priority support',
      'GitHub integration',
      'Private projects',
      'Custom templates',
    ],
    cta: 'Start Pro Trial',
    popular: true,
  },
  {
    name: 'Team',
    price: '$99',
    period: 'per month',
    description: 'For teams building together',
    features: [
      'Everything in Pro',
      'Up to 10 team members',
      'Team collaboration',
      'Shared templates',
      'Admin dashboard',
      'SSO authentication',
      'Dedicated support',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
]

export function Pricing() {
  return (
    <section id="pricing" className="section bg-white">
      <div className="container-custom px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="heading-2 mb-4">Simple, transparent pricing</h2>
          <p className="text-body max-w-2xl mx-auto">
            Start free, upgrade when you need more. No hidden fees.
          </p>
        </div>

        {/* Plans */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-8 ${
                plan.popular
                  ? 'bg-primary text-white ring-4 ring-primary/20'
                  : 'bg-white border border-border'
              }`}
            >
              {plan.popular && (
                <div className="text-sm font-medium mb-4 bg-white/20 rounded-full px-3 py-1 inline-block">
                  Most Popular
                </div>
              )}
              
              <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
              
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className={plan.popular ? 'text-white/70' : 'text-secondary'}>
                  /{plan.period}
                </span>
              </div>
              
              <p className={`mb-6 ${plan.popular ? 'text-white/80' : 'text-secondary'}`}>
                {plan.description}
              </p>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3">
                    <Check className={`w-5 h-5 ${plan.popular ? 'text-white' : 'text-green-500'}`} />
                    <span className={plan.popular ? 'text-white/90' : ''}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <Button
                variant={plan.popular ? 'secondary' : 'primary'}
                className={`w-full ${plan.popular ? 'bg-white text-primary hover:bg-gray-100' : ''}`}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
