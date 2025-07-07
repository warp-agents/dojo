from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router
from .api.v1.schemas import HealthResponse

app = FastAPI(
    title="My LLM API",
    description="An API for various LLM-powered tasks.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production!
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