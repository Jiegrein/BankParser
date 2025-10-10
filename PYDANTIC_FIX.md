# Pydantic Import Error Fix 🔧

## Issue
`BaseSettings` has been moved from `pydantic` to `pydantic-settings` package in Pydantic v2.5+

## Error Message
```
pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package
```

## Fix Applied

### 1. Updated `requirements.txt`
```diff
  pydantic==2.5.0
+ pydantic-settings==2.1.0
```

### 2. Updated `app/config.py`
```diff
- from pydantic import BaseSettings
+ from pydantic_settings import BaseSettings
```

## Quick Fix Steps

1. **Stop current container**:
   ```powershell
   docker stop bankparser-dev
   docker rm bankparser-dev
   ```

2. **Rebuild development image**:
   ```powershell
   docker build -f Dockerfile.dev -t bankparser:dev .
   ```

3. **Start new container**:
   ```powershell
   docker run -d --name bankparser-dev -p 8001:8000 --env-file .env -v ${PWD}:/app bankparser:dev
   ```

4. **Check logs**:
   ```powershell
   docker logs -f bankparser-dev
   ```

## Expected Result
Container should now start successfully with:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using WatchFiles
INFO:     Started server process [X]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Test API
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/health"
```

The fix is now applied - rebuild and restart the container! 🚀