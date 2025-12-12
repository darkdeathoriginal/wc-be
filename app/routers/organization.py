from fastapi import APIRouter, Depends, HTTPException

from app.models import OrgCreateRequest, OrgResponse, OrgUpdateRequest
from app.security import get_current_admin
from app.services import OrganizationService

router = APIRouter(prefix="/org", tags=["Organization"])


@router.post("/create", response_model=OrgResponse)
def create_org(
    data: OrgCreateRequest, service: OrganizationService = Depends(OrganizationService)
):
    return service.create_organization(
        data.organization_name, data.email, data.password
    )


@router.get("/get")
def get_org(
    organization_name: str, service: OrganizationService = Depends(OrganizationService)
):
    return service.get_organization(organization_name)


@router.put("/update", response_model=OrgResponse)
def update_org(
    data: OrgUpdateRequest,
    current_user: dict = Depends(get_current_admin),
    service: OrganizationService = Depends(OrganizationService),
):

    current_org_name = current_user["org_name"]

    return service.update_organization(
        current_org_name=current_org_name,
        new_name=data.organization_name,
        email=data.email,
        password=data.password,
    )


@router.delete("/delete")
def delete_org(
    organization_name: str,
    current_user: dict = Depends(get_current_admin),
    service: OrganizationService = Depends(OrganizationService),
):
    if current_user["org_name"] != organization_name:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this organization"
        )

    return service.delete_organization(organization_name)
