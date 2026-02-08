'use client'

import React from 'react'
import { Check, X } from 'lucide-react'

const comparisons = [
  {
    feature: 'Full-stack generation',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'End-to-end project creation',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'Built-in flows (SaaS, API, Refactor)',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'Automatic Docker setup',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'CI/CD pipeline generation',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'Test suite generation',
    masidy: true,
    copilot: true,
    cursor: true,
    chatgpt: true,
  },
  {
    feature: 'Code completion',
    masidy: true,
    copilot: true,
    cursor: true,
    chatgpt: true,
  },
  {
    feature: 'Live preview',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'Structured execution plan',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
  {
    feature: 'Automatic retries',
    masidy: true,
    copilot: false,
    cursor: false,
    chatgpt: false,
  },
]

export function Comparison() {
  return (
    <section className="section bg-white">
      <div className="container-custom px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="heading-2 mb-4">Why Masidy vs the market</h2>
          <p className="text-body max-w-2xl mx-auto">
            While other tools help you write code, Masidy builds complete, 
            production-ready applications from start to finish.
          </p>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-4 px-4 font-semibold">Feature</th>
                <th className="text-center py-4 px-4">
                  <div className="inline-flex flex-col items-center">
                    <span className="font-bold text-lg">Masidy</span>
                    <span className="text-xs text-accent">You are here</span>
                  </div>
                </th>
                <th className="text-center py-4 px-4 font-semibold text-secondary">Copilot</th>
                <th className="text-center py-4 px-4 font-semibold text-secondary">Cursor</th>
                <th className="text-center py-4 px-4 font-semibold text-secondary">ChatGPT</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((row, index) => (
                <tr key={row.feature} className={index % 2 === 0 ? 'bg-surface' : ''}>
                  <td className="py-4 px-4 font-medium">{row.feature}</td>
                  <td className="text-center py-4 px-4">
                    {row.masidy ? (
                      <Check className="w-5 h-5 text-green-500 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-red-500 mx-auto" />
                    )}
                  </td>
                  <td className="text-center py-4 px-4">
                    {row.copilot ? (
                      <Check className="w-5 h-5 text-green-500 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-red-500 mx-auto" />
                    )}
                  </td>
                  <td className="text-center py-4 px-4">
                    {row.cursor ? (
                      <Check className="w-5 h-5 text-green-500 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-red-500 mx-auto" />
                    )}
                  </td>
                  <td className="text-center py-4 px-4">
                    {row.chatgpt ? (
                      <Check className="w-5 h-5 text-green-500 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-red-500 mx-auto" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
