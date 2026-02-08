const endpoints = [
  {
    category: 'Authentication',
    items: [
      { method: 'POST', path: '/auth/signup', description: 'Create a new user account' },
      { method: 'POST', path: '/auth/login', description: 'Authenticate and receive tokens' },
      { method: 'POST', path: '/auth/refresh', description: 'Refresh access token' },
      { method: 'GET', path: '/auth/me', description: 'Get current user profile' },
    ],
  },
  {
    category: 'Projects',
    items: [
      { method: 'GET', path: '/projects', description: 'List all projects' },
      { method: 'POST', path: '/projects', description: 'Create a new project' },
      { method: 'GET', path: '/projects/{id}', description: 'Get project details' },
      { method: 'PUT', path: '/projects/{id}', description: 'Update project' },
      { method: 'DELETE', path: '/projects/{id}', description: 'Delete project' },
    ],
  },
  {
    category: 'Runs',
    items: [
      { method: 'GET', path: '/projects/{id}/runs', description: 'List runs for a project' },
      { method: 'POST', path: '/projects/{id}/runs', description: 'Create a new run' },
      { method: 'GET', path: '/runs/{id}', description: 'Get run details' },
      { method: 'POST', path: '/runs/{id}/start', description: 'Start run execution' },
      { method: 'POST', path: '/runs/{id}/stop', description: 'Stop run execution' },
    ],
  },
  {
    category: 'Files',
    items: [
      { method: 'GET', path: '/runs/{id}/files', description: 'List generated files' },
      { method: 'GET', path: '/runs/{id}/files/{path}', description: 'Get file content' },
      { method: 'PUT', path: '/runs/{id}/files/{path}', description: 'Update file content' },
    ],
  },
  {
    category: 'Steps',
    items: [
      { method: 'GET', path: '/runs/{id}/steps', description: 'List run steps' },
      { method: 'GET', path: '/steps/{id}', description: 'Get step details' },
      { method: 'GET', path: '/steps/{id}/logs', description: 'Get step logs' },
    ],
  },
]

const methodColors: Record<string, string> = {
  GET: 'bg-green-100 text-green-800',
  POST: 'bg-blue-100 text-blue-800',
  PUT: 'bg-yellow-100 text-yellow-800',
  DELETE: 'bg-red-100 text-red-800',
}

export default function ApiReferencePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">API Reference</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Complete reference for the Masidy REST API.
          </p>
          <div className="flex justify-center gap-4">
            <span className="px-4 py-2 bg-gray-100 rounded-lg font-mono text-sm">
              Base URL: https://api.masidy.com/v1
            </span>
          </div>
        </div>
      </section>

      {/* API Endpoints */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-4xl">
          {/* Authentication */}
          <div className="mb-12 p-6 bg-gray-50 rounded-xl">
            <h2 className="text-xl font-bold mb-4">Authentication</h2>
            <p className="text-gray-600 mb-4">
              All API requests require authentication using a Bearer token in the Authorization header:
            </p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
              <code>Authorization: Bearer your_access_token</code>
            </pre>
          </div>

          {/* Endpoints */}
          <div className="space-y-12">
            {endpoints.map((category, index) => (
              <div key={index}>
                <h2 className="text-2xl font-bold mb-6">{category.category}</h2>
                <div className="space-y-4">
                  {category.items.map((endpoint, endpointIndex) => (
                    <div
                      key={endpointIndex}
                      className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition"
                    >
                      <span className={`px-2 py-1 text-xs font-bold rounded ${methodColors[endpoint.method]}`}>
                        {endpoint.method}
                      </span>
                      <code className="ml-4 font-mono text-sm">{endpoint.path}</code>
                      <span className="ml-auto text-gray-600 text-sm">{endpoint.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Example */}
          <div className="mt-12 p-6 bg-gray-900 rounded-xl">
            <h3 className="text-white font-bold mb-4">Example Request</h3>
            <pre className="text-gray-300 overflow-x-auto">
              <code>{`curl -X POST https://api.masidy.com/v1/projects \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "my-app",
    "description": "Build a task management app"
  }'`}</code>
            </pre>
          </div>
        </div>
      </section>
    </div>
  )
}
