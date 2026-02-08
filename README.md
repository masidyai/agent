# Masidy - AI Agent Platform

<div align="center">

![Masidy Logo](https://img.shields.io/badge/Masidy-AI_Agent_Platform-black?style=for-the-badge)

**Build complete, production-ready applications from a simple prompt.**

[Live Demo](https://masidy.ai) · [Documentation](./docs) · [Report Bug](https://github.com/masidyai/agent/issues)

</div>

---

## ✨ What is Masidy?

Masidy is an all-in-one AI agent platform that builds complete applications end-to-end. Unlike code assistants that help you write code, Masidy creates entire projects - from backend APIs to full-stack SaaS applications - complete with authentication, database, Docker, CI/CD, and more.

### Key Features

- 🚀 **Three Powerful Flows**: SaaS apps, API services, or repository refactoring
- 🤖 **AI-Powered Planning**: Intelligent step-by-step execution with retries
- 🎨 **Modern Web IDE**: Real-time preview, code explorer, and AI builder
- 📦 **Production Ready**: Docker, tests, CI/CD included in every project
- 🔧 **33+ Built-in Tools**: File operations, shell commands, GitHub integration
- ⚡ **Live Execution**: Watch your project being built in real-time

---

## 🏗️ Architecture

```
masidy/
├── masidy_agent_runtime/     # Core Python agent runtime
│   ├── agents/               # AI agent orchestration (Swarm + LangGraph)
│   ├── blueprints/           # Flow templates (SaaS, API, Refactor)
│   ├── executors/            # Structured plan execution with retries
│   ├── flows/                # Flow routing logic
│   ├── tools/                # 33 built-in tools
│   ├── memory/               # State persistence
│   └── main.py               # CLI interface
│
├── masidy_frontend/          # Next.js web application
│   ├── src/
│   │   ├── app/              # Pages (landing, dashboard, IDE)
│   │   ├── components/       # React components
│   │   │   ├── ui/           # Design system (Button, Card, Input...)
│   │   │   ├── layout/       # Header, Footer
│   │   │   ├── landing/      # Landing page sections
│   │   │   ├── dashboard/    # Dashboard components
│   │   │   └── ide/          # Web IDE components
│   │   ├── lib/              # API client, utilities
│   │   └── styles/           # Global CSS + Tailwind
│   └── package.json
│
└── backend_api/              # FastAPI backend server
    ├── main.py               # API endpoints
    └── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository

```bash
git clone https://github.com/masidyai/agent.git
cd agent
```

### 2. Start the Backend API

```bash
cd backend_api
pip install -r requirements.txt
python main.py
```

The API server will start at `http://localhost:8000`

### 3. Start the Frontend

```bash
cd masidy_frontend
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`

### 4. (Optional) Use CLI Directly

```bash
cd masidy_agent_runtime
pip install -r requirements.txt
python main.py --flow saas --task "Build a task management app"
```

---

## 🖥️ Usage

### Web Interface

1. **Landing Page**: Enter your prompt in the hero section
2. **IDE**: The AI Builder analyzes your request and presents a plan
3. **Execution**: Confirm the plan to start building
4. **Result**: View files in the explorer, see live preview

### CLI Interface

```bash
# Build a SaaS application
python main.py --flow saas --task "Build a task management app with user auth"

# Create an API service
python main.py --flow api --task "Create a REST API for notes"

# Refactor a repository
python main.py --flow refactor --task "Modernize this project with Docker and CI/CD"

# With verbose output
python main.py --flow api --task "Build a notes API" --verbose
```

---

## 📦 Available Flows

### SaaS Flow (`--flow saas`)
Generates a complete full-stack SaaS application:
- FastAPI backend with authentication
- SQLite/PostgreSQL database
- React frontend with dashboard
- Docker + docker-compose
- GitHub Actions CI/CD
- 45+ files generated

### API Flow (`--flow api`)
Generates a production-ready REST API:
- FastAPI with Pydantic validation
- SQLAlchemy models
- CRUD endpoints
- Unit tests with pytest
- OpenAPI documentation
- Docker setup
- 33+ files generated

### Refactor Flow (`--flow refactor`)
Modernizes an existing repository:
- Adds Dockerfile and docker-compose
- Creates CI/CD pipeline
- Generates test suite
- Adds pre-commit hooks
- Updates documentation

---

## 🎨 Design System

The frontend uses a consistent design system:

- **Theme**: White background, black text
- **Typography**: Inter font family
- **Components**: Button, Input, Card, Modal
- **Layout**: Responsive with modern SaaS aesthetics

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#000000` | Text, buttons |
| Secondary | `#6b7280` | Muted text |
| Accent | `#3b82f6` | Links, highlights |
| Background | `#ffffff` | Page background |
| Surface | `#f9fafb` | Cards, panels |
| Border | `#e5e7eb` | Dividers |

---

## 🔌 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create new project |
| GET | `/api/projects/{id}` | Get project details |
| POST | `/api/projects/{id}/plan` | Generate execution plan |
| POST | `/api/projects/{id}/execute` | Start execution |
| GET | `/api/executions/{id}/stream` | Stream execution progress (SSE) |
| GET | `/api/flows` | List available flows |
| GET | `/api/tools` | List available tools |

### Example: Create and Execute a Project

```bash
# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a notes API", "flow": "api"}'

# Get execution plan
curl -X POST http://localhost:8000/api/projects/{project_id}/plan

# Start execution
curl -X POST http://localhost:8000/api/projects/{project_id}/execute

# Stream progress
curl http://localhost:8000/api/executions/{execution_id}/stream
```

---

## 🛠️ Development

### Project Structure

```
masidy_frontend/src/
├── app/
│   ├── page.tsx              # Landing page
│   ├── dashboard/page.tsx    # Dashboard
│   └── ide/page.tsx          # Web IDE
├── components/
│   ├── ui/                   # Button, Input, Card, Modal
│   ├── layout/               # Header, Footer
│   ├── landing/              # Hero, Examples, Features, Pricing
│   ├── dashboard/            # Sidebar, ProjectCard
│   └── ide/                  # AIBuilder, FileExplorer, CodeEditor, Preview
└── lib/
    └── api.ts                # API client
```

### Running Tests

```bash
# Backend tests
cd masidy_agent_runtime
pytest

# Frontend tests
cd masidy_frontend
npm test
```

### Building for Production

```bash
# Frontend
cd masidy_frontend
npm run build

# The build output will be in .next/
```

---

## 🗺️ Roadmap

- [ ] Real LLM integration (OpenAI, Claude)
- [ ] GitHub OAuth login
- [ ] Project persistence (database)
- [ ] Collaborative editing
- [ ] Custom flow templates
- [ ] Plugin system for tools
- [ ] Cloud deployment (Vercel, Railway)
- [ ] Project export/download

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI Swarm](https://github.com/openai/swarm) - Agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - Planning loops
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling

---

<div align="center">
  <p>Built with ❤️ by the Masidy team</p>
  <p>
    <a href="https://twitter.com/masidyai">Twitter</a> ·
    <a href="https://github.com/masidyai">GitHub</a> ·
    <a href="https://masidy.ai">Website</a>
  </p>
</div>
