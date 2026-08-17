from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME
from models.personality import PersonalityOut
import pickle
import numpy as np

router = APIRouter(tags=["Personality"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

with open("ml/personality/personality_model.pkl", "rb") as f:
    saved = pickle.load(f)
    personality_model   = saved["model"]
    personality_encoder = saved["encoder"]

PERSONALITY_META = {
    "Speedster": {
        "emoji": "🚀",
        "description": "You finish tasks faster than anyone. Speed is your superpower."
    },
    "Consistency Champion": {
        "emoji": "🔥",
        "description": "Always on time, always present. You are the backbone of the team."
    },
    "Problem Solver": {
        "emoji": "💡",
        "description": "You thrive under pressure and take on the hardest challenges."
    },
    "Multitasker": {
        "emoji": "🎯",
        "description": "You juggle multiple projects effortlessly without dropping the ball."
    },
    "Planner": {
        "emoji": "📈",
        "description": "You work smart, not just hard. Planning is your biggest strength."
    },
    "Balanced Performer": {
        "emoji": "🤝",
        "description": "You bring stability and reliability to everything you work on."
    }
}


@router.get("/employees/{uid}/personality", response_model=PersonalityOut)
async def get_personality(uid: str):
    employee = await db["employees"].find_one({"uid": uid}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tp = await db["task_performance"].find_one({"uid": uid}, {"_id": 0})
    if not tp:
        raise HTTPException(status_code=404, detail="Task performance not found")

    attendance = await db["raw_attendance"].find_one({"uid": uid}, {"_id": 0})
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance data not found")

    # extract features
    tasks      = tp.get("tasks", [])
    done_tasks = [t for t in tasks if t.get("status") == "Done" and t.get("actualHours")]

    tasks_completed    = tp.get("doneTasks", 0)
    avg_completion_hrs = round(
        sum(t["actualHours"] for t in done_tasks) / len(done_tasks), 2
    ) if done_tasks else 0

    present    = attendance.get("presentDays", 0)
    total_days = attendance.get("totalDays", 1)
    att_pct    = round((present / total_days) * 100, 2)

    projects   = len(set(t.get("project") for t in tasks if t.get("project")))
    avg_hours  = attendance.get("avgHours", 0)

    done       = tp.get("doneTasks", 0)
    ontime     = tp.get("onTimeCompletions", 0)
    ontime_pct = round((ontime / done) * 100, 2) if done else 0

    features = np.array([[
        tasks_completed, avg_completion_hrs,
        att_pct, projects, avg_hours, ontime_pct
    ]])

    pred_encoded  = personality_model.predict(features)[0]
    probabilities = personality_model.predict_proba(features)[0]
    personality   = personality_encoder.inverse_transform([pred_encoded])[0]

    prob_dict = {
        personality_encoder.classes_[i]: round(float(probabilities[i]) * 100, 2)
        for i in range(len(personality_encoder.classes_))
    }

    meta = PERSONALITY_META.get(personality, {"emoji": "⭐", "description": ""})

    return {
        "uid": uid,
        "personality": personality,
        "emoji": meta["emoji"],
        "description": meta["description"],
        "probabilities": prob_dict,
        "input_features": {
            "tasks_completed":    tasks_completed,
            "avg_completion_hrs": avg_completion_hrs,
            "attendance":         att_pct,
            "projects":           projects,
            "avg_hours":          avg_hours,
            "ontime_pct":         ontime_pct
        }
    }