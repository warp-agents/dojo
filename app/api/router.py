from fastapi import APIRouter
from .v1 import endpoints as v1_endpoints

api_router = APIRouter()
api_router.include_router(v1_endpoints.router, tags=["v1"])