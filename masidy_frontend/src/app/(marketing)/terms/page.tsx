export default function TermsPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Terms of Service</h1>
          <p className="text-gray-600">Last updated: February 8, 2024</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <article className="prose prose-lg max-w-none">
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using Masidy's services, you agree to be bound by these Terms of 
              Service. If you do not agree to these terms, please do not use our services.
            </p>

            <h2>2. Description of Service</h2>
            <p>
              Masidy provides an AI-powered development platform that helps users generate, 
              review, test, and deploy software applications. Our service includes:
            </p>
            <ul>
              <li>AI code generation from natural language descriptions</li>
              <li>Multi-agent code review and testing</li>
              <li>Deployment automation</li>
              <li>Project management tools</li>
            </ul>

            <h2>3. User Accounts</h2>
            <p>
              To use our services, you must create an account. You are responsible for:
            </p>
            <ul>
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us of any unauthorized use</li>
            </ul>

            <h2>4. Acceptable Use</h2>
            <p>You agree not to use our services to:</p>
            <ul>
              <li>Violate any laws or regulations</li>
              <li>Infringe on intellectual property rights</li>
              <li>Generate malicious software or code</li>
              <li>Harass, abuse, or harm others</li>
              <li>Attempt to gain unauthorized access to our systems</li>
            </ul>

            <h2>5. Intellectual Property</h2>
            <p>
              <strong>Your Content:</strong> You retain ownership of all code and content you 
              create using our platform. By using our service, you grant us a limited license 
              to process your content as necessary to provide our services.
            </p>
            <p>
              <strong>Our Content:</strong> Masidy and its licensors retain all rights to our 
              platform, including software, designs, and documentation.
            </p>

            <h2>6. Payment and Billing</h2>
            <p>
              If you subscribe to a paid plan:
            </p>
            <ul>
              <li>You agree to pay all applicable fees</li>
              <li>Fees are billed in advance on a monthly or annual basis</li>
              <li>Refunds are provided according to our refund policy</li>
              <li>We may change pricing with 30 days notice</li>
            </ul>

            <h2>7. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by law, Masidy shall not be liable for any 
              indirect, incidental, special, consequential, or punitive damages resulting 
              from your use of our services.
            </p>

            <h2>8. Termination</h2>
            <p>
              We may terminate or suspend your account at any time for violation of these 
              terms. You may terminate your account at any time through your account settings.
            </p>

            <h2>9. Changes to Terms</h2>
            <p>
              We may modify these terms at any time. We will notify you of material changes 
              via email or through our platform. Continued use after changes constitutes 
              acceptance of the new terms.
            </p>

            <h2>10. Contact</h2>
            <p>
              For questions about these terms, contact us at legal@masidy.com
            </p>
          </article>
        </div>
      </section>
    </div>
  )
}
