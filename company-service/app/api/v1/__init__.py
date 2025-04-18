from fastapi import APIRouter
from app.api.v1.endpoints import company

api_router = APIRouter()
api_router.include_router(company.router, prefix="/companies", tags=["companies"]) 