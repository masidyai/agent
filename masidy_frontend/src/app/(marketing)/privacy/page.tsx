export default function PrivacyPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Privacy Policy</h1>
          <p className="text-gray-600">Last updated: February 8, 2024</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <article className="prose prose-lg max-w-none">
            <h2>1. Introduction</h2>
            <p>
              Masidy, Inc. ("Masidy," "we," "us," or "our") respects your privacy and is committed 
              to protecting your personal data. This privacy policy explains how we collect, use, 
              and share information about you when you use our services.
            </p>

            <h2>2. Information We Collect</h2>
            <h3>Information you provide:</h3>
            <ul>
              <li>Account information (name, email, password)</li>
              <li>Project data and code you create using our platform</li>
              <li>Payment information for billing purposes</li>
              <li>Communications with our support team</li>
            </ul>

            <h3>Information collected automatically:</h3>
            <ul>
              <li>Usage data (features used, time spent)</li>
              <li>Device information (browser, operating system)</li>
              <li>Log data (IP address, access times)</li>
            </ul>

            <h2>3. How We Use Your Information</h2>
            <p>We use the information we collect to:</p>
            <ul>
              <li>Provide and maintain our services</li>
              <li>Improve and personalize your experience</li>
              <li>Process payments and transactions</li>
              <li>Communicate with you about our services</li>
              <li>Ensure security and prevent fraud</li>
            </ul>

            <h2>4. How We Share Your Information</h2>
            <p>
              We do not sell your personal information. We may share information with:
            </p>
            <ul>
              <li>Service providers who assist in operating our platform</li>
              <li>Legal authorities when required by law</li>
              <li>Business partners with your consent</li>
            </ul>

            <h2>5. Data Security</h2>
            <p>
              We implement industry-standard security measures to protect your data, including 
              encryption, access controls, and regular security audits.
            </p>

            <h2>6. Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Delete your data</li>
              <li>Export your data</li>
              <li>Opt-out of marketing communications</li>
            </ul>

            <h2>7. Contact Us</h2>
            <p>
              If you have questions about this privacy policy, please contact us at:
            </p>
            <p>
              <strong>Email:</strong> privacy@masidy.com<br />
              <strong>Address:</strong> 548 Market St #35410, San Francisco, CA 94104
            </p>
          </article>
        </div>
      </section>
    </div>
  )
}
