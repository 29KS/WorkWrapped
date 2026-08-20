from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from backend.config import MONGO_URI, DB_NAME
from backend.models.personality import PersonalityOut

import pickle
import numpy as np
from pathlib import Path


router = APIRouter(tags=["Personality"])


# --------------------------------------------------
# Database
# --------------------------------------------------

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


# --------------------------------------------------
# Model path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "personality"
    / "personality_model.pkl"
)


# --------------------------------------------------
# Load model
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Personality model not found at: {MODEL_PATH}"
    )


with open(MODEL_PATH, "rb") as f:
    saved = pickle.load(f)

personality_model = saved["model"]
personality_encoder = saved["encoder"]


# --------------------------------------------------
# Personality metadata
# --------------------------------------------------

PERSONALITY_META = {

    "Speedster": {
        "emoji": "🚀",
        "description":
            "You finish tasks faster than anyone. "
            "Speed is your superpower."
    },

    "Consistency Champion": {
        "emoji": "🔥",
        "description":
            "Always on time, always present. "
            "You are the backbone of the team."
    },

    "Problem Solver": {
        "emoji": "💡",
        "description":
            "You thrive under pressure and take "
            "on the hardest challenges."
    },

    "Multitasker": {
        "emoji": "🎯",
        "description":
            "You juggle multiple projects effortlessly "
            "without dropping the ball."
    },

    "Planner": {
        "emoji": "📈",
        "description":
            "You work smart, not just hard. "
            "Planning is your biggest strength."
    },

    "Balanced Performer": {
        "emoji": "🤝",
        "description":
            "You bring stability and reliability "
            "to everything you work on."
    }
}


# --------------------------------------------------
# Endpoint
# --------------------------------------------------

@router.get(
    "/employees/{uid}/personality",
    response_model=PersonalityOut
)
async def get_personality(uid: str):

    employee = await db["employees"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )


    tp = await db["task_performance"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not tp:
        raise HTTPException(
            status_code=404,
            detail="Task performance not found"
        )


    attendance = await db["raw_attendance"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance data not found"
        )


    # --------------------------------------------------
    # Task features
    # --------------------------------------------------

    tasks = tp.get(
        "tasks",
        []
    )

    done_tasks = [
        t for t in tasks
        if t.get("status") == "Done"
        and t.get("actualHours") is not None
    ]


    tasks_completed = tp.get(
        "doneTasks",
        0
    )


    if done_tasks:

        avg_completion_hrs = round(
            sum(
                t["actualHours"]
                for t in done_tasks
            ) / len(done_tasks),
            2
        )

    else:
        avg_completion_hrs = 0


    # --------------------------------------------------
    # Attendance
    # --------------------------------------------------

    present = attendance.get(
        "presentDays",
        0
    )

    total_days = attendance.get(
        "totalDays",
        1
    )

    if total_days <= 0:
        total_days = 1


    att_pct = round(
        (present / total_days) * 100,
        2
    )


    # --------------------------------------------------
    # Projects
    # --------------------------------------------------

    projects = len(
        set(
            t.get("project")
            for t in tasks
            if t.get("project")
        )
    )


    avg_hours = attendance.get(
        "avgHours",
        0
    )


    # --------------------------------------------------
    # On-time percentage
    # --------------------------------------------------

    done = tp.get(
        "doneTasks",
        0
    )

    ontime = tp.get(
        "onTimeCompletions",
        0
    )


    if done > 0:

        ontime_pct = round(
            (ontime / done) * 100,
            2
        )

    else:
        ontime_pct = 0


    # --------------------------------------------------
    # Model input
    # --------------------------------------------------

    features = np.array([[
        tasks_completed,
        avg_completion_hrs,
        att_pct,
        projects,
        avg_hours,
        ontime_pct
    ]])


    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    pred_encoded = personality_model.predict(
        features
    )[0]

    probabilities = personality_model.predict_proba(
        features
    )[0]

    personality = personality_encoder.inverse_transform(
        [pred_encoded]
    )[0]


    # --------------------------------------------------
    # Probabilities
    # --------------------------------------------------

    prob_dict = {
        personality_encoder.classes_[i]:
        round(
            float(probabilities[i]) * 100,
            2
        )
        for i in range(
            len(personality_encoder.classes_)
        )
    }


    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    meta = PERSONALITY_META.get(
        personality,
        {
            "emoji": "⭐",
            "description": ""
        }
    )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "uid": uid,
        "personality": personality,
        "emoji": meta["emoji"],
        "description": meta["description"],
        "probabilities": prob_dict,

        "input_features": {
            "tasks_completed": tasks_completed,
            "avg_completion_hrs": avg_completion_hrs,
            "attendance": att_pct,
            "projects": projects,
            "avg_hours": avg_hours,
            "ontime_pct": ontime_pct
        }
    }