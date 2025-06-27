# FastAPI Backend v2

This is the new FastAPI backend for the Restaurant Marketing Platform, designed to replace the existing Node.js backend.

## Phase 1A: Basic Setup

This phase implements a minimal FastAPI server with health check functionality.

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backendv2
pip install -r requirements.txt
```

### 2. Start the Development Server

```bash
python run.py
```

The server will start on `http://localhost:8000`

### 3. Test the Setup

#### Health Check Endpoint
- **URL**: `http://localhost:8000/api/health`
- **Method**: GET
- **Expected Response**:
```json
{
  "status": "healthy",
  "message": "FastAPI Backend v2 is running",
  "version": "2.0.0"
}
```

#### Root Endpoint
- **URL**: `http://localhost:8000/`
- **Method**: GET
- **Expected Response**:
```json
{
  "message": "Welcome to Restaurant Marketing Platform API v2",
  "docs": "/docs",
  "health": "/api/health"
}
```

#### Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing Criteria

✅ FastAPI server starts without errors  
✅ Health check endpoint returns 200 status  
✅ Server runs on port 8000 (different from Node.js server on port 5000)  
✅ Can access http://localhost:8000/api/health and get JSON response  

## Project Structure

```
backendv2/
├── app/
│   ├── __init__.py
│   └── main.py          # Main FastAPI application
├── requirements.txt     # Python dependencies
├── run.py              # Development server startup script
└── README.md           # This file
```

## Next Steps

After Phase 1A is validated:
- Phase 1B: Add MongoDB connection
- Phase 1C: Add authentication endpoints
- Phase 2: Migrate existing API endpoints