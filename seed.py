import json
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "effitrack"
DATA_FOLDER = "data"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_one(db, raw):
    uid = raw["profile"]["uid"]
    print(f"\nSeeding: {uid}")

    # employees
    if not await db["employees"].find_one({"uid": uid}):
        await db["employees"].insert_one(raw["profile"])
        print(f"  Inserted employee: {uid}")
    else:
        print(f"  Employee already exists, skipping.")

    # task_performance
    if not await db["task_performance"].find_one({"uid": uid}):
        data = raw["taskPerformance"]
        data["uid"] = uid
        await db["task_performance"].insert_one(data)
        print(f"  Inserted task performance: {uid}")
    else:
        print(f"  Task performance already exists, skipping.")

    # raw_attendance
    if not await db["raw_attendance"].find_one({"uid": uid}):
        data = raw["attendance"]
        data["uid"] = uid
        await db["raw_attendance"].insert_one(data)
        print(f"  Inserted attendance: {uid}")
    else:
        print(f"  Attendance already exists, skipping.")

    # projects
    if not await db["projects"].find_one({"uid": uid}):
        await db["projects"].insert_one({
            "uid": uid,
            "priorProjects": raw["profile"].get("priorProjects", [])
        })
        print(f"  Inserted projects: {uid}")
    else:
        print(f"  Projects already exist, skipping.")

    # auth account — seeded automatically, no registration needed
    if not await db["users"].find_one({"uid": uid}):
        email = raw["profile"].get("email", "")
        # default password = first part of email before @
        default_password = email.split("@")[0][:72]  # truncate to 72 bytes max
        await db["users"].insert_one({
            "uid": uid,
            "email": email,
            "hashed_password": pwd_context.hash(default_password),
            "role": raw["profile"].get("role", "intern").lower()
    })
    print(f"  Created auth account: {email} / password: {default_password}")


async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    files = list(Path(DATA_FOLDER).glob("*.json"))
    if not files:
        print("No JSON files found in data/ folder.")
        return

    print(f"Found {len(files)} file(s): {[f.name for f in files]}")
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        await seed_one(db, raw)

    client.close()
    print("\nAll done.")


if __name__ == "__main__":
    asyncio.run(seed())