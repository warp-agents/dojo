from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router
from .api.v1.schemas import HealthResponse

app = FastAPI(
    title="Warp Dojo",
    description="AI Agent training ground.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # your dev origin
        "http://127.0.0.1:3000",
        "https://playground-gcvm.onrender.com"  # plus any prod domains
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix="/api")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Performs a health check of the API."""
    return {"status": "healthy", "message": "FastAPI server is running"}