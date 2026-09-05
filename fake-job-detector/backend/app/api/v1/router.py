from fastapi import APIRouter
from app.api.v1 import analysis, auth, community, health, verification_certificate, educational

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(analysis.router)
api_v1_router.include_router(community.router)
api_v1_router.include_router(verification_certificate.router)
api_v1_router.include_router(educational.router)

