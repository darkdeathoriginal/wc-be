from fastapi import APIRouter, Depends

from app.models import LoginRequest, Token
from app.services import OrganizationService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=Token)
def login(
    creds: LoginRequest,
    service: OrganizationService = Depends(OrganizationService),
):
    return service.authenticate_admin(creds.email, creds.password)
