from typing import Optional

from pydantic import BaseModel, EmailStr


class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str


class OrgUpdateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str


class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
