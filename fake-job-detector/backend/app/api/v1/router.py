from fastapi import APIRouter
from app.api.v1 import analysis, auth, community, educational, health, verification_certificate

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(analysis.router)
api_v1_router.include_router(community.router)
api_v1_router.include_router(verification_certificate.router)
api_v1_router.include_router(educational.router)

