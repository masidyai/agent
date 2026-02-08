'use client'

import { useState } from 'react'

const integrations = [
  {
    id: 'github',
    name: 'GitHub',
    description: 'Connect your GitHub account to push code directly to repositories.',
    icon: '🐙',
    connected: false,
  },
  {
    id: 'vercel',
    name: 'Vercel',
    description: 'Deploy your projects to Vercel with one click.',
    icon: '▲',
    connected: false,
  },
  {
    id: 'railway',
    name: 'Railway',
    description: 'Deploy backend services to Railway infrastructure.',
    icon: '🚂',
    connected: false,
  },
  {
    id: 'stripe',
    name: 'Stripe',
    description: 'Integrate Stripe for payment processing in your projects.',
    icon: '💳',
    connected: false,
  },
  {
    id: 'supabase',
    name: 'Supabase',
    description: 'Use Supabase for authentication and database.',
    icon: '⚡',
    connected: false,
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Get notifications about your projects in Slack.',
    icon: '💬',
    connected: false,
  },
]

export default function IntegrationsPage() {
  const [connections, setConnections] = useState<Record<string, boolean>>({})
  const [connecting, setConnecting] = useState<string | null>(null)

  const handleConnect = async (integrationId: string) => {
    setConnecting(integrationId)
    
    // Simulate OAuth flow
    setTimeout(() => {
      setConnections({ ...connections, [integrationId]: true })
      setConnecting(null)
    }, 1500)
  }

  const handleDisconnect = async (integrationId: string) => {
    if (!confirm('Are you sure you want to disconnect this integration?')) return
    setConnections({ ...connections, [integrationId]: false })
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">Integrations</h1>
      <p className="text-gray-600 mb-8">Connect third-party services to enhance your workflow.</p>

      <div className="grid md:grid-cols-2 gap-6">
        {integrations.map((integration) => {
          const isConnected = connections[integration.id]
          const isConnecting = connecting === integration.id

          return (
            <div
              key={integration.id}
              className="bg-white rounded-xl border border-gray-200 p-6"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{integration.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">{integration.name}</h3>
                    {isConnected && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        Connected
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{integration.description}</p>
                  
                  {isConnected ? (
                    <button
                      onClick={() => handleDisconnect(integration.id)}
                      className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition"
                    >
                      Disconnect
                    </button>
                  ) : (
                    <button
                      onClick={() => handleConnect(integration.id)}
                      disabled={isConnecting}
                      className="px-4 py-2 bg-black text-white rounded-lg text-sm hover:bg-gray-800 transition disabled:opacity-50"
                    >
                      {isConnecting ? 'Connecting...' : 'Connect'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Custom Webhooks */}
      <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-semibold mb-4">Custom Webhooks</h3>
        <p className="text-gray-600 mb-4">
          Send events to your own endpoints when projects are created, builds complete, or deployments finish.
        </p>
        <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition">
          Add Webhook
        </button>
      </div>
    </div>
  )
}
