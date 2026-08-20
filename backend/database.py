from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

employee_collection = db["employees"]