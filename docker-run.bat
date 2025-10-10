@echo off
REM Windows batch script for Docker operations

set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

echo %BLUE%🐳 Bank Statement Parser - Docker Setup%NC%
echo ========================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Docker is not running. Please start Docker and try again.%NC%
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo %YELLOW%⚠️  .env file not found. Creating from template...%NC%
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo %YELLOW%📝 Please edit .env file and add your OpenAI API key%NC%
)

REM Parse command
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=help

if "%COMMAND%"=="build" goto build
if "%COMMAND%"=="run" goto run
if "%COMMAND%"=="dev" goto dev
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="logs" goto logs
if "%COMMAND%"=="shell" goto shell
if "%COMMAND%"=="clean" goto clean
if "%COMMAND%"=="test" goto test
goto help

:build
echo %BLUE%🔨 Building Docker image...%NC%
docker build -t bankparser:latest .
docker build -t bankparser:dev -f Dockerfile.dev .
echo %GREEN%✅ Build completed!%NC%
goto end

:run
echo %BLUE%🚀 Starting production container...%NC%
docker-compose up -d bankparser
echo %GREEN%✅ Production server started!%NC%
echo %YELLOW%📍 API: http://localhost:8000%NC%
echo %YELLOW%📚 Docs: http://localhost:8000/docs%NC%
goto end

:dev
echo %BLUE%🛠️  Starting development container...%NC%
docker-compose --profile dev up -d bankparser-dev
echo %GREEN%✅ Development server started with hot reload!%NC%
echo %YELLOW%📍 API: http://localhost:8001%NC%
echo %YELLOW%📚 Docs: http://localhost:8001/docs%NC%
echo %YELLOW%🔄 Code changes will auto-reload%NC%
goto end

:stop
echo %BLUE%🛑 Stopping containers...%NC%
docker-compose down
echo %GREEN%✅ All containers stopped!%NC%
goto end

:logs
set SERVICE=%2
if "%SERVICE%"=="" set SERVICE=bankparser
echo %BLUE%📋 Showing logs for %SERVICE%...%NC%
docker-compose logs -f %SERVICE%
goto end

:shell
set CONTAINER=%2
if "%CONTAINER%"=="" set CONTAINER=bankparser
echo %BLUE%🐚 Opening shell in %CONTAINER%...%NC%
docker-compose exec %CONTAINER% /bin/bash
goto end

:clean
echo %BLUE%🧹 Cleaning up containers and images...%NC%
docker-compose down -v
docker rmi bankparser:latest bankparser:dev 2>nul
echo %GREEN%✅ Cleanup completed!%NC%
goto end

:test
echo %BLUE%🧪 Running tests in container...%NC%
docker-compose exec bankparser-dev python -m pytest
goto end

:help
echo %BLUE%Usage:%NC%
echo   %0 [COMMAND]
echo.
echo %BLUE%Commands:%NC%
echo   build       Build the Docker image
echo   run         Run the production container
echo   dev         Run the development container with hot reload
echo   stop        Stop all running containers
echo   logs        Show container logs
echo   shell       Open shell in running container
echo   clean       Remove containers and images
echo   test        Run tests in container
echo.
echo %BLUE%Examples:%NC%
echo   %0 dev      # Start development server with hot reload
echo   %0 run      # Start production server
echo   %0 logs     # View logs

:end