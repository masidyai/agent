import type { Metadata } from 'next'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'Masidy - AI Agent Platform for Building Applications',
  description: 'Build complete, production-ready applications from a simple prompt. SaaS apps, APIs, and more — in minutes.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
