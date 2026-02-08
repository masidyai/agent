'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiKey {
  id: string
  name: string
  key: string
  created_at: string
  last_used: string | null
}

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKey, setNewKey] = useState<string | null>(null)

  useEffect(() => {
    fetchKeys()
  }, [])

  const fetchKeys = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/api/auth/api-keys`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setKeys(data)
      }
    } catch (err) {
      console.error('Failed to fetch API keys:', err)
    } finally {
      setLoading(false)
    }
  }

  const createKey = async () => {
    if (!newKeyName.trim()) return

    setCreating(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/api/auth/api-keys`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newKeyName }),
      })

      if (response.ok) {
        const data = await response.json()
        setNewKey(data.key)
        setKeys([data, ...keys])
        setNewKeyName('')
      }
    } catch (err) {
      console.error('Failed to create API key:', err)
    } finally {
      setCreating(false)
    }
  }

  const deleteKey = async (id: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) return

    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${API_URL}/api/auth/api-keys/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      setKeys(keys.filter(k => k.id !== id))
    } catch (err) {
      console.error('Failed to delete API key:', err)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">API Keys</h1>
      <p className="text-gray-600 mb-8">Manage your API keys for programmatic access to Masidy.</p>

      {/* New Key Created */}
      {newKey && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="font-semibold text-green-800 mb-2">API Key Created!</h3>
          <p className="text-sm text-green-700 mb-3">
            Make sure to copy your API key now. You won't be able to see it again!
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 p-3 bg-white border border-green-300 rounded font-mono text-sm">
              {newKey}
            </code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              Copy
            </button>
          </div>
          <button
            onClick={() => setNewKey(null)}
            className="mt-3 text-sm text-green-700 hover:underline"
          >
            I've saved my key
          </button>
        </div>
      )}

      {/* Create New Key */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h3 className="font-semibold mb-4">Create New API Key</h3>
        <div className="flex gap-4">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Key name (e.g., Production, Development)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
          />
          <button
            onClick={createKey}
            disabled={creating || !newKeyName.trim()}
            className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Create Key'}
          </button>
        </div>
      </div>

      {/* Existing Keys */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="font-semibold">Your API Keys</h3>
        </div>
        
        {loading ? (
          <div className="p-6">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-center justify-between py-4 border-b border-gray-100 last:border-0 animate-pulse">
                <div>
                  <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-48" />
                </div>
                <div className="h-8 bg-gray-200 rounded w-16" />
              </div>
            ))}
          </div>
        ) : keys.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {keys.map((key) => (
              <div key={key.id} className="p-6 flex items-center justify-between">
                <div>
                  <h4 className="font-medium">{key.name}</h4>
                  <p className="text-sm text-gray-500">
                    Created {formatDate(key.created_at)}
                    {key.last_used && ` • Last used ${formatDate(key.last_used)}`}
                  </p>
                  <code className="text-sm text-gray-400 font-mono">
                    {key.key.substring(0, 8)}...{key.key.substring(key.key.length - 4)}
                  </code>
                </div>
                <button
                  onClick={() => deleteKey(key.id)}
                  className="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition"
                >
                  Revoke
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <div className="text-4xl mb-4">🔑</div>
            <h4 className="font-semibold mb-2">No API Keys</h4>
            <p className="text-gray-500">Create your first API key to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
