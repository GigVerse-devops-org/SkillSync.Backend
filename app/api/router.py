from fastapi import APIRouter
from app.api.v1.auth.auth import router as auth_router
from api.v1.auth.verification import router as verification_router

router = APIRouter()
router.include_router(auth_router, tags=["auth"])
router.include_router(verification_router, tags=["verify"])