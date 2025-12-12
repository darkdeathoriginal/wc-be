from fastapi import FastAPI

from app.database import db
from app.routers import admin, organization

app = FastAPI(title="Multi-Tenant Backend")


@app.on_event("startup")
def startup_db_client():
    db.connect()


@app.on_event("shutdown")
def shutdown_db_client():
    db.close()


app.include_router(organization.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Multi-tenant Service Running"}
