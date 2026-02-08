export default function CookiesPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Cookie Policy</h1>
          <p className="text-gray-600">Last updated: February 8, 2024</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-3xl">
          <article className="prose prose-lg max-w-none">
            <h2>What Are Cookies?</h2>
            <p>
              Cookies are small text files stored on your device when you visit a website. 
              They help websites remember your preferences and improve your experience.
            </p>

            <h2>How We Use Cookies</h2>
            <p>Masidy uses cookies for the following purposes:</p>

            <h3>Essential Cookies</h3>
            <p>
              These cookies are necessary for the website to function properly. They enable 
              core functionality such as:
            </p>
            <ul>
              <li>User authentication and session management</li>
              <li>Security features</li>
              <li>Remembering your preferences</li>
            </ul>

            <h3>Analytics Cookies</h3>
            <p>
              We use analytics cookies to understand how visitors interact with our website. 
              This helps us improve our services. Analytics cookies collect:
            </p>
            <ul>
              <li>Pages visited and time spent</li>
              <li>Features used</li>
              <li>Error reports</li>
            </ul>

            <h3>Functional Cookies</h3>
            <p>
              These cookies enable enhanced functionality and personalization:
            </p>
            <ul>
              <li>Language preferences</li>
              <li>Theme settings (light/dark mode)</li>
              <li>Recently viewed projects</li>
            </ul>

            <h2>Third-Party Cookies</h2>
            <p>
              We may use third-party services that set their own cookies:
            </p>
            <ul>
              <li><strong>Stripe:</strong> For payment processing</li>
              <li><strong>Google Analytics:</strong> For usage analytics</li>
              <li><strong>Intercom:</strong> For customer support</li>
            </ul>

            <h2>Managing Cookies</h2>
            <p>
              You can control cookies through your browser settings. Most browsers allow you to:
            </p>
            <ul>
              <li>View what cookies are stored</li>
              <li>Delete cookies</li>
              <li>Block cookies from specific sites</li>
              <li>Block all cookies</li>
            </ul>
            <p>
              Note: Blocking essential cookies may prevent you from using some features of our service.
            </p>

            <h2>Cookie Retention</h2>
            <table>
              <thead>
                <tr>
                  <th>Cookie Type</th>
                  <th>Retention Period</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Session cookies</td>
                  <td>Until browser is closed</td>
                </tr>
                <tr>
                  <td>Authentication cookies</td>
                  <td>7-30 days</td>
                </tr>
                <tr>
                  <td>Analytics cookies</td>
                  <td>2 years</td>
                </tr>
                <tr>
                  <td>Preference cookies</td>
                  <td>1 year</td>
                </tr>
              </tbody>
            </table>

            <h2>Contact Us</h2>
            <p>
              If you have questions about our use of cookies, please contact us at 
              privacy@masidy.com
            </p>
          </article>
        </div>
      </section>
    </div>
  )
}
