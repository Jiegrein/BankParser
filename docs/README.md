# Documentation

Documentation for the Bank Statement Parser project.

## Core Documentation

### [CLAUDE.md](CLAUDE.md)
Comprehensive guide for AI assistants (like Claude Code) working with this codebase. Includes:
- Common commands for running, testing, and deploying
- Architecture overview and design patterns
- LLM service architecture details
- Configuration management
- Implementation details and best practices

### [ADDING_NEW_LLMS.md](ADDING_NEW_LLMS.md)
Developer guide for adding new LLM providers. Includes:
- 3-step integration process
- Architecture benefits (SOLID principles)
- Complete examples (Ollama, Claude, Gemini)
- A/B testing and fallback strategies
- Real-world integration patterns

### [DOCKER.md](DOCKER.md)
Complete Docker deployment guide. Includes:
- Quick start instructions
- Development vs production modes
- Docker Compose usage
- Container management commands
- Platform-specific syntax (Linux/Mac/Windows)
- Troubleshooting Docker issues

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Common issues and solutions. Covers:
- Docker-related issues
- Pydantic configuration problems
- LLM API errors and JSON parsing
- PDF processing issues
- File upload problems
- Performance optimization tips

## Quick Links

- **API Documentation**: Run the app and visit http://localhost:8000/docs
- **Main README**: [../README.md](../README.md)
- **Requirements**: [../requirements.txt](../requirements.txt)

## Document Purpose Guide

| Need to... | Read This |
|-----------|-----------|
| Understand the codebase architecture | [CLAUDE.md](CLAUDE.md) |
| Add a new LLM provider (Gemini, Claude, etc.) | [ADDING_NEW_LLMS.md](ADDING_NEW_LLMS.md) |
| Deploy with Docker | [DOCKER.md](DOCKER.md) |
| Fix an error or issue | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Get started quickly | [../README.md](../README.md) |
| Work with AI assistants on this code | [CLAUDE.md](CLAUDE.md) |
