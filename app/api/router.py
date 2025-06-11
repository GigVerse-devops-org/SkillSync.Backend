from fastapi import APIRouter
from .profile import router as profile_router

router = APIRouter()
router.include_router(profile_router, tags=["profile"])