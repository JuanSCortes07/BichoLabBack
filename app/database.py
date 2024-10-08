from google.cloud import firestore
from google.cloud import storage
from app.auth import get_gcp_credentials
from pathlib import Path

BUCKET_NAME = "insects_id"
credentials_data = get_gcp_credentials(credentials_file=str(Path("config") / "insect-clasification-fc57888c0cfe.json"))

# Inicializa la conexión a Firestore
async def get_database():
    db = firestore.AsyncClient(credentials=credentials_data)
    return db

async def get_bucket():
    storage_client = storage.Client(credentials=credentials_data)
    bucket = storage_client.bucket(BUCKET_NAME)
    return bucket
    
