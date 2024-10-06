'''from motor.motor_asyncio import AsyncIOMotorClient

async def get_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["insectID_database"]
    return db'''

from google.cloud import firestore
from google.cloud import storage

BUCKET_NAME = "insects_id"

# Inicializa la conexión a Firestore
async def get_database():
    db = firestore.AsyncClient()
    return db

async def get_bucket():
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    return bucket
    
