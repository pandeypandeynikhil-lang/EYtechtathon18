# backend/app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import analysis

api_router = APIRouter()
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
