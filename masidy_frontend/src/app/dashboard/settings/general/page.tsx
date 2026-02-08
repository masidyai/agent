'use client'

import { useState, useEffect } from 'react'

export default function GeneralSettingsPage() {
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'America/Los_Angeles',
    notifications: {
      email: true,
      browser: true,
      projectUpdates: true,
      marketing: false,
    },
    editor: {
      fontSize: 14,
      tabSize: 2,
      wordWrap: true,
      minimap: true,
    },
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSave = async () => {
    setSaving(true)
    try {
      // Save to localStorage and/or API
      localStorage.setItem('settings', JSON.stringify(settings))
      setMessage('Settings saved successfully!')
    } catch (err) {
      setMessage('Failed to save settings')
    } finally {
      setSaving(false)
      setTimeout(() => setMessage(''), 3000)
    }
  }

  useEffect(() => {
    const saved = localStorage.getItem('settings')
    if (saved) {
      try {
        setSettings(JSON.parse(saved))
      } catch (e) {
        // Use defaults
      }
    }
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">General Settings</h1>
      <p className="text-gray-600 mb-8">Customize your Masidy experience.</p>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${message.includes('success') ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {message}
        </div>
      )}

      <div className="space-y-8 max-w-2xl">
        {/* Appearance */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold mb-4">Appearance</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Language</label>
              <select
                value={settings.language}
                onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
                <option value="ja">日本語</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Europe/Paris">Paris (CET)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold mb-4">Notifications</h3>
          
          <div className="space-y-4">
            {[
              { key: 'email', label: 'Email notifications', description: 'Receive updates via email' },
              { key: 'browser', label: 'Browser notifications', description: 'Show desktop notifications' },
              { key: 'projectUpdates', label: 'Project updates', description: 'Get notified when builds complete' },
              { key: 'marketing', label: 'Marketing emails', description: 'Tips, news, and product updates' },
            ].map((item) => (
              <label key={item.key} className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications[item.key as keyof typeof settings.notifications]}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, [item.key]: e.target.checked }
                  })}
                  className="mt-1 h-4 w-4 rounded border-gray-300 text-black focus:ring-black"
                />
                <div className="ml-3">
                  <p className="font-medium">{item.label}</p>
                  <p className="text-sm text-gray-500">{item.description}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Editor Preferences */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold mb-4">Editor Preferences</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Font Size</label>
              <input
                type="number"
                min="10"
                max="24"
                value={settings.editor.fontSize}
                onChange={(e) => setSettings({
                  ...settings,
                  editor: { ...settings.editor, fontSize: parseInt(e.target.value) }
                })}
                className="w-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Tab Size</label>
              <select
                value={settings.editor.tabSize}
                onChange={(e) => setSettings({
                  ...settings,
                  editor: { ...settings.editor, tabSize: parseInt(e.target.value) }
                })}
                className="w-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="2">2 spaces</option>
                <option value="4">4 spaces</option>
              </select>
            </div>

            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.editor.wordWrap}
                onChange={(e) => setSettings({
                  ...settings,
                  editor: { ...settings.editor, wordWrap: e.target.checked }
                })}
                className="h-4 w-4 rounded border-gray-300 text-black focus:ring-black"
              />
              <span className="ml-3">Word wrap</span>
            </label>

            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.editor.minimap}
                onChange={(e) => setSettings({
                  ...settings,
                  editor: { ...settings.editor, minimap: e.target.checked }
                })}
                className="h-4 w-4 rounded border-gray-300 text-black focus:ring-black"
              />
              <span className="ml-3">Show minimap</span>
            </label>
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
