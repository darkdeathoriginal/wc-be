from pymongo import MongoClient

from app.config import settings


class Database:
    client: MongoClient = None

    @classmethod
    def connect(cls):

        if cls.client is None:
            cls.client = MongoClient(settings.MONGO_URI)
            print("Connected to MongoDB via Serverless")

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            cls.client = None

    @classmethod
    def get_master_db(cls):

        if cls.client is None:
            cls.connect()
        return cls.client[settings.MASTER_DB_NAME]

    @classmethod
    def get_dynamic_collection(cls, org_collection_name: str):
        if cls.client is None:
            cls.connect()
        return cls.client[settings.MASTER_DB_NAME][org_collection_name]


db = Database()
