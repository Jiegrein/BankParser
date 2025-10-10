# 🐳 Docker Deployment Guide

Simple guide to run the Bank Statement Parser API using Docker.

## 📋 Prerequisites

- Docker installed and running
- OpenAI API key

## 🚀 Quick Start

### 1. Setup Environment Variables
Create or edit your `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### 2. Build the Docker Image
```bash
docker build -t bankparser .
```

### 3. Run the Container

#### Linux/Mac/WSL:
```bash
docker run -d \
  --name bankparser \
  -p 8000:8000 \
  --env-file .env \
  bankparser
```

#### Windows PowerShell:
```powershell
docker run -d --name bankparser -p 8000:8000 --env-file .env bankparser
```

### 4. Access the API
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🛠️ Development Mode

For development with hot reload:

### Build Development Image
```bash
docker build -f Dockerfile.dev -t bankparser:dev .
```

### Run Development Container

#### Linux/Mac/WSL:
```bash
docker run -d \
  --name bankparser-dev \
  -p 8001:8000 \
  --env-file .env \
  -v $(pwd):/app \
  bankparser:dev
```

#### Windows PowerShell:
```powershell
docker run -d --name bankparser-dev -p 8001:8000 --env-file .env -v ${PWD}:/app bankparser:dev
```

#### Windows CMD:
```cmd
docker run -d --name bankparser-dev -p 8001:8000 --env-file .env -v %cd%:/app bankparser:dev
```

Access at: http://localhost:8001

## 🐙 Using Docker Compose

### Production
```bash
docker-compose up -d bankparser
```

### Development
```bash
docker-compose --profile dev up -d bankparser-dev
```

### With Nginx (Production)
```bash
docker-compose --profile production up -d
```

## 📊 Container Management

### View Logs
```bash
docker logs bankparser
# or
docker-compose logs bankparser
```

### Stop Container
```bash
docker stop bankparser
# or
docker-compose down
```

### Container Shell Access

#### Linux/Mac/WSL:
```bash
docker exec -it bankparser /bin/bash
```

#### Windows:
```powershell
docker exec -it bankparser /bin/bash
```

### Check Container Status
```bash
docker ps
docker inspect bankparser
```

## 🧪 Test the Deployment

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Windows PowerShell (if curl not available):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
```

### Upload Test (with a PDF file)

#### Linux/Mac/WSL:
```bash
curl -X POST "http://localhost:8000/api/v1/parse-statement" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_statement.pdf" \
     -F "use_vision=true" \
     -F "llm_provider=openai"
```

#### Windows PowerShell:
```powershell
$form = @{
    file = Get-Item "your_statement.pdf"
    use_vision = "true"
    llm_provider = "openai"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/parse-statement" -Method Post -Form $form
```

### Check Supported Formats
```bash
curl http://localhost:8000/api/v1/supported-formats
```

## 🔧 Configuration Options

### Environment Variables
```env
# Required
OPENAI_API_KEY=your_key_here

# Optional Configuration
DEBUG=False                    # Enable/disable debug mode
HOST=0.0.0.0                  # Server host
PORT=8000                     # Server port
MAX_FILE_SIZE_MB=10           # Maximum upload size
MODEL_NAME=gpt-4-vision-preview # OpenAI model
MAX_TOKENS=4000               # Max tokens for LLM
TEMPERATURE=0.1               # LLM temperature
```

### Port Mapping
```bash
# Map to different host port
docker run -p 9000:8000 bankparser  # Access on port 9000
```

### Volume Mounts

#### Linux/Mac/WSL:
```bash
# Mount config directory
docker run -v $(pwd)/config:/app/config bankparser

# Mount uploads directory  
docker run -v $(pwd)/uploads:/app/uploads bankparser
```

#### Windows PowerShell:
```powershell
# Mount config directory
docker run -v ${PWD}/config:/app/config bankparser

# Mount uploads directory  
docker run -v ${PWD}/uploads:/app/uploads bankparser
```

#### Windows CMD:
```cmd
# Mount config directory
docker run -v %cd%/config:/app/config bankparser

# Mount uploads directory  
docker run -v %cd%/uploads:/app/uploads bankparser
```

## 🔒 Security Considerations

- Container runs as non-root user (`appuser`)
- File size limits enforced (10MB default)
- Health checks enabled
- CORS configured
- Environment variables for secrets

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs bankparser

# Check if port is available (Linux/Mac)
netstat -tlnp | grep 8000

# Check if port is available (Windows)
netstat -an | findstr :8000

# Verify environment variables
docker exec bankparser env | grep OPENAI
```

### Permission Issues (Linux/Mac/WSL)
```bash
# Check container user
docker exec bankparser whoami

# Fix file permissions if needed
docker exec bankparser chown -R appuser:appuser /app
```

### API Not Responding
```bash
# Test internal connectivity
docker exec bankparser curl localhost:8000/api/v1/health

# Check container networking
docker inspect bankparser | grep IPAddress
```

### Windows-Specific Issues

#### Volume Mounting Not Working
Make sure Docker Desktop has access to your drive:
1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Add your drive (e.g., C:)
4. Apply & Restart

#### PowerShell Execution Policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🏗️ Docker Files Overview

- **`Dockerfile`**: Production image (optimized, secure)
- **`Dockerfile.dev`**: Development image (dev tools, hot reload)
- **`docker-compose.yml`**: Multi-service setup
- **`.dockerignore`**: Excludes unnecessary files from build

## 📦 Image Details

### Production Image (`Dockerfile`)
- Base: `python:3.11-slim`
- Size: ~200MB
- Features: Optimized, security hardened, health checks
- User: Non-root (`appuser`)

### Development Image (`Dockerfile.dev`)
- Base: `python:3.11-slim`
- Size: ~250MB
- Features: Dev tools, hot reload, debugging
- Use: Development and testing

## 🔄 Updating the Application

### Rebuild and Restart
```bash
# Stop current container
docker stop bankparser

# Rebuild image
docker build -t bankparser .

# Remove old container
docker rm bankparser

# Start new container (Linux/Mac/WSL)
docker run -d --name bankparser -p 8000:8000 --env-file .env bankparser
```

#### Windows PowerShell:
```powershell
# Stop and remove
docker stop bankparser
docker rm bankparser

# Rebuild and start
docker build -t bankparser .
docker run -d --name bankparser -p 8000:8000 --env-file .env bankparser
```

### Using Docker Compose
```bash
# Rebuild and restart
docker-compose up -d --build bankparser
```

## 📈 Production Deployment

### Basic Production Setup

#### Linux/Mac/WSL:
```bash
# 1. Set production environment
export OPENAI_API_KEY=your_production_key
export DEBUG=False

# 2. Build production image
docker build -t bankparser:prod .

# 3. Run with production settings
docker run -d \
  --name bankparser-prod \
  -p 80:8000 \
  --restart unless-stopped \
  --env OPENAI_API_KEY=$OPENAI_API_KEY \
  --env DEBUG=False \
  bankparser:prod
```

#### Windows PowerShell:
```powershell
# 1. Set production environment
$env:OPENAI_API_KEY="your_production_key"
$env:DEBUG="False"

# 2. Build production image
docker build -t bankparser:prod .

# 3. Run with production settings
docker run -d --name bankparser-prod -p 80:8000 --restart unless-stopped --env OPENAI_API_KEY=$env:OPENAI_API_KEY --env DEBUG=False bankparser:prod
```

### With Reverse Proxy (Nginx)
The included `nginx.conf` provides:
- Rate limiting (10 req/sec)
- Large file uploads (20MB)
- Health check proxying
- Production-ready settings

## 🎯 Quick Commands Reference

### Linux/Mac/WSL:
```bash
# Build
docker build -t bankparser .

# Run
docker run -d --name bankparser -p 8000:8000 --env-file .env bankparser

# Logs
docker logs -f bankparser

# Stop
docker stop bankparser

# Remove
docker rm bankparser

# Shell
docker exec -it bankparser /bin/bash

# Health Check
curl http://localhost:8000/api/v1/health
```

### Windows PowerShell:
```powershell
# Build
docker build -t bankparser .

# Run
docker run -d --name bankparser -p 8000:8000 --env-file .env bankparser

# Logs
docker logs -f bankparser

# Stop
docker stop bankparser

# Remove
docker rm bankparser

# Shell
docker exec -it bankparser /bin/bash

# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
```

## 🖥️ Platform-Specific Volume Syntax

| Platform | Current Directory Syntax | Example |
|----------|--------------------------|---------|
| Linux/Mac/WSL | `$(pwd)` | `docker run -v $(pwd):/app` |
| Windows PowerShell | `${PWD}` | `docker run -v ${PWD}:/app` |
| Windows CMD | `%cd%` | `docker run -v %cd%:/app` |

That's it! Your Bank Statement Parser is now running in Docker! 🎉