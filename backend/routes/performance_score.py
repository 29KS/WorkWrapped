from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DB_NAME
from backend.models.performance_score import PerformanceScoreOut

from pathlib import Path
import pickle
import numpy as np


router = APIRouter(tags=["Performance Score"])


# --------------------------------------------------
# Database
# --------------------------------------------------

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


# --------------------------------------------------
# Load ML Model
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "score"
    / "score_model.pkl"
)


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Score model not found at: {MODEL_PATH}"
    )


with open(MODEL_PATH, "rb") as f:
    saved = pickle.load(f)

score_model = saved["model"]
model_name = saved["model_name"]


# --------------------------------------------------
# Grade Calculation
# --------------------------------------------------

def get_grade(score: float):

    if score >= 90:
        return "A+", "#2ecc71"

    elif score >= 80:
        return "A", "#27ae60"

    elif score >= 70:
        return "B", "#f39c12"

    elif score >= 60:
        return "C", "#e67e22"

    else:
        return "D", "#e74c3c"


# --------------------------------------------------
# Feature Contribution
# --------------------------------------------------

def get_contribution(features: dict) -> dict:

    tips = {}


    # Attendance
    if features["attendance"] >= 95:

        tips["Attendance"] = "🟢 Excellent"

    elif features["attendance"] >= 80:

        tips["Attendance"] = "🟡 Good"

    else:

        tips["Attendance"] = "🔴 Needs Improvement"


    # Task Completion
    if features["completion"] >= 90:

        tips["Task Completion"] = "🟢 Excellent"

    elif features["completion"] >= 70:

        tips["Task Completion"] = "🟡 Good"

    else:

        tips["Task Completion"] = "🔴 Needs Improvement"


    # Punctuality
    if features["late_arrivals"] <= 2:

        tips["Punctuality"] = "🟢 Excellent"

    elif features["late_arrivals"] <= 6:

        tips["Punctuality"] = "🟡 Moderate"

    else:

        tips["Punctuality"] = "🔴 High Late Arrivals"


    # Working Hours
    if features["hours"] >= 8:

        tips["Working Hours"] = "🟢 On Track"

    elif features["hours"] >= 6:

        tips["Working Hours"] = "🟡 Below Average"

    else:

        tips["Working Hours"] = "🔴 Low Hours"


    # Projects
    if features["projects"] >= 5:

        tips["Projects"] = "🟢 High Involvement"

    elif features["projects"] >= 3:

        tips["Projects"] = "🟡 Moderate"

    else:

        tips["Projects"] = "🔴 Low Involvement"


    return tips


# --------------------------------------------------
# Performance Score Prediction
# --------------------------------------------------

@router.get(
    "/employees/{uid}/performance-score",
    response_model=PerformanceScoreOut
)
async def predict_performance_score(uid: str):

    # ----------------------------------------------
    # Employee
    # ----------------------------------------------

    employee = await db["employees"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )


    # ----------------------------------------------
    # Attendance
    # ----------------------------------------------

    attendance = await db["raw_attendance"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance data not found"
        )


    # ----------------------------------------------
    # Task Performance
    # ----------------------------------------------

    tp = await db["task_performance"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not tp:
        raise HTTPException(
            status_code=404,
            detail="Task performance not found"
        )


    # ----------------------------------------------
    # Attendance Percentage
    # ----------------------------------------------

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


    attendance_pct = round(
        (present / total_days) * 100,
        2
    )


    # ----------------------------------------------
    # Task Completion
    # ----------------------------------------------

    done = tp.get(
        "doneTasks",
        0
    )

    total = tp.get(
        "totalTasks",
        1
    )

    if total <= 0:
        total = 1


    completion_rate = round(
        (done / total) * 100,
        2
    )


    # ----------------------------------------------
    # Projects
    # ----------------------------------------------

    tasks = tp.get(
        "tasks",
        []
    )

    projects = len(
        set(
            task.get("project")
            for task in tasks
            if task.get("project")
        )
    )


    # ----------------------------------------------
    # Other Features
    # ----------------------------------------------

    avg_hours = attendance.get(
        "avgHours",
        0
    )

    late_arrivals = attendance.get(
        "lateArrivals",
        0
    )


    # ----------------------------------------------
    # Feature Dictionary
    # ----------------------------------------------

    features = {

        "attendance":
            attendance_pct,

        "completion":
            completion_rate,

        "projects":
            projects,

        "hours":
            avg_hours,

        "late_arrivals":
            late_arrivals
    }


    # ----------------------------------------------
    # Prepare ML Input
    # ----------------------------------------------

    X = np.array([
        [
            features["attendance"],
            features["completion"],
            features["projects"],
            features["hours"],
            features["late_arrivals"]
        ]
    ])


    # ----------------------------------------------
    # Prediction
    # ----------------------------------------------

    predicted = float(
        np.clip(
            score_model.predict(X)[0],
            0,
            100
        )
    )

    predicted = round(
        predicted,
        2
    )


    # ----------------------------------------------
    # Grade
    # ----------------------------------------------

    grade, grade_color = get_grade(
        predicted
    )


    # ----------------------------------------------
    # Response
    # ----------------------------------------------

    return {

        "uid":
            uid,

        "predicted_score":
            predicted,

        "grade":
            grade,

        "grade_color":
            grade_color,

        "model_used":
            model_name,

        "input_features":
            features,

        "feature_contribution":
            get_contribution(features)
    }