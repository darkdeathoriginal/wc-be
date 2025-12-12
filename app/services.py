import pymongo
from fastapi import HTTPException, status

from app.database import db
from app.security import SecurityHandler


class OrganizationService:
    def __init__(self):
        self.master_db = db.get_master_db()
        self.org_collection = self.master_db["organizations"]
        self.users_collection = self.master_db["users"]

    def create_organization(self, org_name: str, email: str, password: str):

        if self.org_collection.find_one({"name": org_name}):
            raise HTTPException(status_code=400, detail="Organization already exists")

        if self.users_collection.find_one({"email": email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = SecurityHandler.get_password_hash(password)
        user_doc = {
            "email": email,
            "password": hashed_password,
            "org_name": org_name,
            "role": "admin",
        }
        self.users_collection.insert_one(user_doc)

        collection_name = f"org_{org_name}"
        org_doc = {
            "name": org_name,
            "collection_name": collection_name,
            "admin_email": email,
        }
        self.org_collection.insert_one(org_doc)

        dynamic_col = db.get_dynamic_collection(collection_name)
        dynamic_col.insert_one({"type": "config", "created_at": str(datetime.now())})

        return {
            "organization_name": org_name,
            "collection_name": collection_name,
            "admin_email": email,
            "message": "Organization created successfully",
        }

    def get_organization(self, org_name: str):
        org = self.org_collection.find_one({"name": org_name}, {"_id": 0})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    def update_organization(
        self, current_org_name: str, new_name: str, email: str, password: str
    ):

        user = self.users_collection.find_one(
            {"email": email, "org_name": current_org_name}
        )
        if not user or not SecurityHandler.verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid admin credentials")

        if current_org_name == new_name:
            return {"message": "No changes detected in organization name"}

        if self.org_collection.find_one({"name": new_name}):
            raise HTTPException(
                status_code=400, detail="New organization name already exists"
            )

        org_metadata = self.org_collection.find_one({"name": current_org_name})
        old_collection_name = org_metadata["collection_name"]
        new_collection_name = f"org_{new_name}"

        try:
            self.master_db[old_collection_name].rename(new_collection_name)
        except pymongo.errors.OperationFailure:

            pass

        self.org_collection.update_one(
            {"name": current_org_name},
            {"$set": {"name": new_name, "collection_name": new_collection_name}},
        )
        self.users_collection.update_many(
            {"org_name": current_org_name}, {"$set": {"org_name": new_name}}
        )

        return {
            "organization_name": new_name,
            "collection_name": new_collection_name,
            "admin_email": email,
            "message": "Organization updated and data migrated",
        }

    def delete_organization(self, org_name: str):

        org_metadata = self.org_collection.find_one({"name": org_name})
        if not org_metadata:
            raise HTTPException(status_code=404, detail="Organization not found")

        collection_name = org_metadata["collection_name"]
        self.master_db.drop_collection(collection_name)

        self.org_collection.delete_one({"name": org_name})
        self.users_collection.delete_many({"org_name": org_name})

        return {"message": f"Organization {org_name} and its data deleted successfully"}

    def authenticate_admin(self, email: str, password: str):
        user = self.users_collection.find_one({"email": email})
        if not user or not SecurityHandler.verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = SecurityHandler.create_access_token(
            data={"sub": user["email"], "org_name": user["org_name"]}
        )
        return {"access_token": access_token, "token_type": "bearer"}


from datetime import datetime
