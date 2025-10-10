#!/bin/bash

# Build and run the Bank Statement Parser with Docker

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Bank Statement Parser - Docker Setup${NC}"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env .env.example 2>/dev/null || echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo -e "${YELLOW}📝 Please edit .env file and add your OpenAI API key${NC}"
fi

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 [COMMAND]"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  build       Build the Docker image"
    echo "  run         Run the production container"
    echo "  dev         Run the development container with hot reload"
    echo "  stop        Stop all running containers"
    echo "  logs        Show container logs"
    echo "  shell       Open shell in running container"
    echo "  clean       Remove containers and images"
    echo "  test        Run tests in container"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 dev      # Start development server with hot reload"
    echo "  $0 run      # Start production server"
    echo "  $0 logs     # View logs"
}

# Parse command
COMMAND=${1:-help}

case $COMMAND in
    "build")
        echo -e "${BLUE}🔨 Building Docker image...${NC}"
        docker build -t bankparser:latest .
        docker build -t bankparser:dev -f Dockerfile.dev .
        echo -e "${GREEN}✅ Build completed!${NC}"
        ;;
    
    "run")
        echo -e "${BLUE}🚀 Starting production container...${NC}"
        docker-compose up -d bankparser
        echo -e "${GREEN}✅ Production server started!${NC}"
        echo -e "${YELLOW}📍 API: http://localhost:8000${NC}"
        echo -e "${YELLOW}📚 Docs: http://localhost:8000/docs${NC}"
        ;;
    
    "dev")
        echo -e "${BLUE}🛠️  Starting development container...${NC}"
        docker-compose --profile dev up -d bankparser-dev
        echo -e "${GREEN}✅ Development server started with hot reload!${NC}"
        echo -e "${YELLOW}📍 API: http://localhost:8001${NC}"
        echo -e "${YELLOW}📚 Docs: http://localhost:8001/docs${NC}"
        echo -e "${YELLOW}🔄 Code changes will auto-reload${NC}"
        ;;
    
    "stop")
        echo -e "${BLUE}🛑 Stopping containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ All containers stopped!${NC}"
        ;;
    
    "logs")
        SERVICE=${2:-bankparser}
        echo -e "${BLUE}📋 Showing logs for $SERVICE...${NC}"
        docker-compose logs -f $SERVICE
        ;;
    
    "shell")
        CONTAINER=${2:-bankparser}
        echo -e "${BLUE}🐚 Opening shell in $CONTAINER...${NC}"
        docker-compose exec $CONTAINER /bin/bash
        ;;
    
    "clean")
        echo -e "${BLUE}🧹 Cleaning up containers and images...${NC}"
        docker-compose down -v
        docker rmi bankparser:latest bankparser:dev 2>/dev/null || true
        echo -e "${GREEN}✅ Cleanup completed!${NC}"
        ;;
    
    "test")
        echo -e "${BLUE}🧪 Running tests in container...${NC}"
        docker-compose exec bankparser-dev python -m pytest
        ;;
    
    "help"|*)
        show_usage
        ;;
esac