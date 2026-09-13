from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router
from app.api.v1.photos import router as photos_router
from app.api.v1.galleries import router as galleries_router
from app.api.v1.public import router as public_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(events_router)
api_router.include_router(photos_router)
api_router.include_router(galleries_router)
api_router.include_router(public_router)
