from fastapi import APIRouter
from app.api.endpoints import registro

api_router = APIRouter()
api_router.include_router(router=registro.router, prefix="/registros", tags=["registros"])