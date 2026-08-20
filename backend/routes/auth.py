from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from backend.config import MONGO_URI, DB_NAME
from backend.models.auth import LoginRequest, TokenOut
from backend.middleware.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login", response_model=TokenOut)
async def login(request: LoginRequest):
    user = await db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(request.password[:72], user["hashed_password"]):
     raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "uid": user["uid"],
        "role": user["role"],
        "email": user["email"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "uid": user["uid"],
        "role": user["role"],
        "email": user["email"]
    }


@router.get("/me")
async def get_me(uid: str, role: str):
    user = await db["users"].find_one({"uid": uid}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user