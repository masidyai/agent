'use client'

import { useState } from 'react'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // In production, this would send to backend
    console.log('Form submitted:', formData)
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Contact Us</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Have a question or feedback? We'd love to hear from you.
          </p>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            {/* Form */}
            <div>
              {submitted ? (
                <div className="p-8 bg-green-50 border border-green-200 rounded-xl text-center">
                  <div className="text-4xl mb-4">✅</div>
                  <h3 className="text-xl font-semibold mb-2">Message Sent!</h3>
                  <p className="text-gray-600">We'll get back to you within 24 hours.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Name</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Subject</label>
                    <select
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select a subject</option>
                      <option value="general">General Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="sales">Sales</option>
                      <option value="partnership">Partnership</option>
                      <option value="press">Press</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Message</label>
                    <textarea
                      required
                      rows={5}
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black resize-none"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
                  >
                    Send Message
                  </button>
                </form>
              )}
            </div>

            {/* Contact Info */}
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">Get in Touch</h3>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <span className="text-2xl mr-4">📧</span>
                    <div>
                      <p className="font-medium">Email</p>
                      <a href="mailto:hello@masidy.com" className="text-gray-600 hover:text-black">
                        hello@masidy.com
                      </a>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="text-2xl mr-4">💬</span>
                    <div>
                      <p className="font-medium">Discord</p>
                      <a href="https://discord.gg/masidy" className="text-gray-600 hover:text-black">
                        Join our community
                      </a>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="text-2xl mr-4">🐦</span>
                    <div>
                      <p className="font-medium">Twitter</p>
                      <a href="https://twitter.com/masidy" className="text-gray-600 hover:text-black">
                        @masidy
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Support</h3>
                <p className="text-gray-600 mb-4">
                  For technical support, check our documentation first. If you still need help, 
                  our support team is available 24/7.
                </p>
                <a href="/docs" className="text-black font-medium hover:underline">
                  View Documentation →
                </a>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Office</h3>
                <p className="text-gray-600">
                  Masidy, Inc.<br />
                  548 Market St #35410<br />
                  San Francisco, CA 94104
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
