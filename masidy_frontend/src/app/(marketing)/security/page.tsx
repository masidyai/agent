export default function SecurityPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Security</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            How we protect your data and ensure platform security.
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <article className="prose prose-lg max-w-none">
            <h2>Our Commitment to Security</h2>
            <p>
              At Masidy, security is a top priority. We implement comprehensive security 
              measures to protect your code, data, and account.
            </p>

            <h2>Infrastructure Security</h2>
            <ul>
              <li><strong>Encryption:</strong> All data is encrypted in transit (TLS 1.3) and at rest (AES-256)</li>
              <li><strong>Cloud Infrastructure:</strong> We use AWS with SOC 2 Type II compliance</li>
              <li><strong>Network Security:</strong> Firewalls, DDoS protection, and intrusion detection</li>
              <li><strong>Regular Audits:</strong> Third-party security assessments annually</li>
            </ul>

            <h2>Application Security</h2>
            <ul>
              <li><strong>Authentication:</strong> Secure password hashing, MFA support, OAuth</li>
              <li><strong>Authorization:</strong> Role-based access control (RBAC)</li>
              <li><strong>Session Management:</strong> Secure session handling with automatic expiration</li>
              <li><strong>Input Validation:</strong> Comprehensive input sanitization</li>
            </ul>

            <h2>Code Security</h2>
            <ul>
              <li><strong>Sandboxed Execution:</strong> All code runs in isolated containers</li>
              <li><strong>No Persistent Access:</strong> Generated code doesn't have access to other users' data</li>
              <li><strong>Secure Defaults:</strong> AI generates code with security best practices</li>
            </ul>

            <h2>Data Protection</h2>
            <ul>
              <li><strong>Data Isolation:</strong> Each user's data is logically separated</li>
              <li><strong>Backups:</strong> Regular encrypted backups with geo-redundancy</li>
              <li><strong>Data Retention:</strong> Clear policies for data retention and deletion</li>
              <li><strong>GDPR Compliance:</strong> Full compliance with EU data protection regulations</li>
            </ul>

            <h2>Compliance</h2>
            <p>Masidy maintains compliance with:</p>
            <ul>
              <li>SOC 2 Type II</li>
              <li>GDPR</li>
              <li>CCPA</li>
            </ul>

            <h2>Vulnerability Disclosure</h2>
            <p>
              We maintain a responsible disclosure program. If you discover a security 
              vulnerability, please report it to:
            </p>
            <p>
              <strong>Email:</strong> security@masidy.com
            </p>
            <p>
              We will acknowledge receipt within 24 hours and work with you to understand 
              and address the issue.
            </p>

            <h2>Security Updates</h2>
            <p>
              We continuously monitor for security threats and release patches promptly. 
              Critical security updates are applied automatically.
            </p>
          </article>
        </div>
      </section>
    </div>
  )
}
