'use client'

import { Header, Footer } from '@/components/layout'
import { 
  Hero, 
  Examples, 
  Features, 
  Comparison, 
  Testimonials, 
  Pricing, 
  Newsletter 
} from '@/components/landing'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Hero />
        <Examples />
        <Features />
        <Comparison />
        <Testimonials />
        <Pricing />
        <Newsletter />
      </main>
      <Footer />
    </div>
  )
}
