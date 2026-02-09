# Docker-Based Code Execution System

## Overview

The Masidy platform now includes a complete Docker-based code execution system that safely runs generated projects in isolated containers. This system validates, builds, tests, and executes code with comprehensive error handling and real-time monitoring.

## Features

### 🔒 Security & Isolation
- **Docker containerization** - Each execution runs in an isolated container
- **Resource limits** - Configurable memory (default: 512MB) and CPU (default: 1 core)
- **Timeout protection** - Automatic termination after configurable timeout (default: 5 minutes)
- **Network isolation** - Optional network disabling for enhanced security
- **Automatic cleanup** - Containers removed after execution

### 🚀 Multi-Language Support
- **Python** - pip dependencies, pytest tests, Python 3.11
- **Node.js** - npm dependencies, npm test, Node 20
- **TypeScript** - ts-node execution with Node 20

### 📋 Execution Pipeline

Each execution goes through these phases:

1. **Validation** - Verify project structure and required files
2. **Build** - Install dependencies (pip install / npm install)
3. **Lint** - Run code quality checks (flake8 / eslint)
4. **Test** - Execute unit tests (pytest / npm test)
5. **Execute** - Run the application (main.py / npm start)
6. **Cleanup** - Remove containers and temporary files

### 📊 Comprehensive Tracking

The system tracks:
- Build status, output, and errors
- Lint status, output, and issues
- Test status, output, passed/failed counts, coverage
- Execution output, errors, exit codes
- Performance metrics (execution time, memory usage, CPU usage)
- Container information (ID, image)

## API Endpoints

### List Executions
```http
GET /api/executions/?project_id={uuid}
```

**Response:**
```json
{
  "executions": [...],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

### Create Execution
```http
POST /api/executions/?project_id={uuid}
Content-Type: application/json

{
  "language": "python",
  "command": "python main.py"
}
```

**Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "pending",
  "language": "python",
  ...
}
```

### Run Execution
```http
POST /api/executions/{execution_id}/run
Content-Type: application/json

{
  "language": "python",
  "timeout": 300
}
```

This starts the execution in the background and returns immediately.

### Get Execution Status
```http
GET /api/executions/{execution_id}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "running",
  "current_phase": "test",
  "build_status": "passed",
  "test_status": "running",
  "tests_passed": 5,
  "tests_failed": 0,
  ...
}
```

### Get Execution Logs
```http
GET /api/executions/{execution_id}/logs
```

**Response:**
```json
{
  "execution_id": "uuid",
  "logs": "=== BUILD OUTPUT ===\n...\n=== TEST OUTPUT ===\n...",
  "timestamp": "2026-02-09T01:30:00Z"
}
```

### Stop Execution
```http
POST /api/executions/{execution_id}/stop
```

Kills the running container and updates status to "cancelled".

### Health Check
```http
GET /api/executions/{execution_id}/health
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "running",
  "is_running": true,
  "uptime_seconds": 45
}
```

## Database Schema

### Executions Table

```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    language VARCHAR(50),
    command TEXT,
    status VARCHAR(50),  -- pending, building, linting, testing, running, success, failed, timeout, cancelled
    current_phase VARCHAR(50),  -- validation, build, lint, test, execution, cleanup
    
    -- Build phase
    build_status VARCHAR(50),
    build_output TEXT,
    build_error TEXT,
    
    -- Lint phase
    lint_status VARCHAR(50),
    lint_output TEXT,
    lint_issues JSON,
    
    -- Test phase
    test_status VARCHAR(50),
    test_output TEXT,
    tests_passed INTEGER,
    tests_failed INTEGER,
    test_coverage FLOAT,
    
    -- Execution phase
    execution_output TEXT,
    execution_error TEXT,
    exit_code INTEGER,
    
    -- Errors
    validation_errors JSON,
    runtime_errors JSON,
    
    -- Metrics
    execution_time_ms INTEGER,
    memory_used_mb INTEGER,
    cpu_usage_percent FLOAT,
    
    -- Docker
    container_id VARCHAR(255),
    container_image VARCHAR(255),
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Configuration

Environment variables in `.env`:

```bash
# Docker Execution Settings
DOCKER_HOST=unix:///var/run/docker.sock  # Docker daemon socket
EXECUTION_TIMEOUT=300                     # Timeout in seconds (5 min)
MAX_MEMORY=512                            # Memory limit in MB
MAX_CPU=1.0                               # CPU limit in cores
KEEP_CONTAINERS=false                     # Debug: keep containers after execution
```

## Usage Examples

### Python Example

1. **Create a project** with these files:

```
my_project/
├── main.py
├── requirements.txt
└── test_main.py
```

2. **Create execution:**
```bash
curl -X POST http://localhost:8000/api/executions/?project_id={project_id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}'
```

3. **Run execution:**
```bash
curl -X POST http://localhost:8000/api/executions/{execution_id}/run \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "timeout": 300}'
```

4. **Monitor status:**
```bash
curl http://localhost:8000/api/executions/{execution_id} \
  -H "Authorization: Bearer {token}"
```

5. **Get logs:**
```bash
curl http://localhost:8000/api/executions/{execution_id}/logs \
  -H "Authorization: Bearer {token}"
```

### Node.js Example

1. **Create a project** with these files:

```
my_project/
├── package.json
├── index.js
└── test/
    └── test.js
```

2. Follow the same API flow as Python, but set `"language": "javascript"`

## Error Handling

The system captures errors at every phase:

### Validation Errors
- Missing required files (package.json, main.py, etc.)
- Invalid project structure

### Build Errors
- Dependency installation failures
- Missing packages
- Version conflicts

### Lint Errors
- Code quality issues
- Style violations

### Test Errors
- Test failures with stack traces
- Coverage below threshold

### Runtime Errors
- Application crashes
- Unhandled exceptions
- Timeout errors

All errors are stored in the database and returned via the API.

## Resource Management

### Memory Limits
Set via `MAX_MEMORY` environment variable (in MB). Container will be killed if it exceeds this limit.

### CPU Limits
Set via `MAX_CPU` environment variable (number of cores). Uses Docker's nano_cpus for precise control.

### Timeout Protection
Set via `EXECUTION_TIMEOUT` environment variable (in seconds). Container automatically killed after timeout.

### Cleanup
Containers are automatically removed after execution unless `KEEP_CONTAINERS=true` is set for debugging.

## Monitoring & Metrics

Track execution performance with:
- **Execution time** - Total time from start to completion
- **Memory usage** - Peak memory consumption
- **CPU usage** - CPU utilization percentage
- **Phase timings** - Time spent in each pipeline phase

## Troubleshooting

### Container Won't Start
- Check Docker daemon is running: `docker ps`
- Verify Docker socket: `ls -l /var/run/docker.sock`
- Check permissions: User must have access to Docker socket

### Timeout Errors
- Increase `EXECUTION_TIMEOUT` for long-running tasks
- Check if application has infinite loops
- Verify dependencies install quickly

### Memory Errors
- Increase `MAX_MEMORY` for memory-intensive applications
- Optimize code to use less memory
- Check for memory leaks

### Build Failures
- Verify requirements.txt or package.json is valid
- Check if all dependencies are available
- Review build logs for specific errors

## Best Practices

1. **Set appropriate timeouts** - Match timeout to expected execution time
2. **Use resource limits** - Prevent runaway processes
3. **Monitor executions** - Check status regularly during long runs
4. **Review logs** - Check all phase outputs for warnings
5. **Test locally** - Verify project structure before execution
6. **Handle errors** - Implement proper error handling in generated code

## Security Considerations

1. **Container isolation** - Each execution runs in a separate container
2. **Resource limits** - Prevents DOS attacks via resource exhaustion
3. **Timeout protection** - Automatic termination of long-running processes
4. **Network isolation** - Can disable network access for enhanced security
5. **Cleanup** - Automatic removal of containers prevents resource leaks
6. **Billing limits** - Execution count tracked and limited by plan

## Future Enhancements

- [ ] Real-time log streaming via WebSockets
- [ ] GPU support for ML workloads
- [ ] Custom Docker images per project
- [ ] Execution scheduling and queuing
- [ ] Execution replays and debugging
- [ ] Performance profiling and optimization suggestions
- [ ] Multi-stage builds for complex projects
- [ ] Health checks for long-running services
- [ ] Automatic retry on transient failures
- [ ] Execution history and analytics
