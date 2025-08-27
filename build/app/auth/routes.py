from fastapi import APIRouter, Depends  # type: ignore

from app.auth.oauth import get_token, OAuth2ClientCredentialsRequestForm

# Add prefix to match the tokenUrl in oauth.py
router = APIRouter(tags=["Authentication"])

@router.post("/token")
async def login_for_access_token(form_data: OAuth2ClientCredentialsRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint for client credentials flow.
    """
    return await get_token(form_data)

# Made with Bob