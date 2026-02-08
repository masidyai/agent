'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProfilePage() {
  const [user, setUser] = useState({
    name: '',
    email: '',
    avatar: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchUser()
  }, [])

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setUser(data)
      }
    } catch (err) {
      console.error('Failed to fetch user:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/api/auth/me`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
      })

      if (response.ok) {
        setMessage('Profile updated successfully!')
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        setMessage('Failed to update profile')
      }
    } catch (err) {
      setMessage('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8" />
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
            <div className="h-10 bg-gray-200 rounded mb-4" />
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
            <div className="h-10 bg-gray-200 rounded" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Profile Settings</h1>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${message.includes('success') ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {message}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 max-w-2xl">
        {/* Avatar */}
        <div className="flex items-center gap-6 mb-8 pb-8 border-b border-gray-200">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center text-2xl">
            {user.name?.charAt(0) || '👤'}
          </div>
          <div>
            <h3 className="font-semibold mb-1">Profile Picture</h3>
            <p className="text-sm text-gray-500 mb-2">JPG, PNG or GIF. Max 2MB.</p>
            <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition">
              Upload Photo
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={user.name}
              onChange={(e) => setUser({ ...user, name: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Email Address</label>
            <input
              type="email"
              value={user.email}
              onChange={(e) => setUser({ ...user, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-xl border border-red-200 p-6 max-w-2xl mt-8">
        <h3 className="text-lg font-semibold text-red-600 mb-2">Danger Zone</h3>
        <p className="text-gray-600 mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg text-sm hover:bg-red-50 transition">
          Delete Account
        </button>
      </div>
    </div>
  )
}
