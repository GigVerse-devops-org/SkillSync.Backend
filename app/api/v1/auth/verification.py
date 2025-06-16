from fastapi import APIRouter, HTTPException

from app.api.v1.auth.schemas import PhoneVerificationRequest, VerificationResponse
from app.infrastructure.supabase_client import SupabaseClient

router = APIRouter()
supabase_client = SupabaseClient.get_instance()

@router.post("/verify/email/resend", summary="Resend verification email")
async def resend_email_verification(email: str):
    """Resend email verification link."""
    try:
        await supabase_client.auth.resend_signup_email(email)
        return {
            "success": True,
            "message": "Verification email sent successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to resend verification email"
        )

@router.post("/verify/phone", response_model=VerificationResponse)
async def verify_phone(request: PhoneVerificationRequest, otp: str):
    """Verify phone number with OTP."""
    try:
        response = await supabase_client.auth.verify_otp({
            "phone": request.phone,
            "token": otp
        })
        
        if not response.user:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OTP"
            )
            
        return VerificationResponse(
            success=True,
            message="Phone Number verified successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify/phone/resend", response_model=VerificationResponse)
async def resend_phone_verification(
    request: PhoneVerificationRequest
):
    """Resend phone verification OTP."""
    try:
        await supabase_client.auth.sign_in_with_otp({
            "phone": request.phone
        })
        
        return VerificationResponse(
            success=True,
            message="OTP sent successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )