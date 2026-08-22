from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from backend.config import MONGO_URI, DB_NAME
from backend.models.burnout import BurnoutOut

import pickle
import numpy as np
from pathlib import Path


router = APIRouter(tags=["Burnout"])


# --------------------------------------------------
# Database
# --------------------------------------------------

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


# --------------------------------------------------
# Model path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "burnout"
    / "burnout_model.pkl"
)


# --------------------------------------------------
# Load model
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Burnout model not found at: {MODEL_PATH}"
    )


with open(MODEL_PATH, "rb") as f:
    saved = pickle.load(f)

model = saved["model"]
encoder = saved["encoder"]


# --------------------------------------------------
# Risk labels
# --------------------------------------------------

RISK_EMOJI = {
    "Low": "🟢 Low Risk",
    "Medium": "🟡 Medium Risk",
    "High": "🔴 High Risk"
}


# --------------------------------------------------
# Endpoint
# --------------------------------------------------

@router.get(
    "/employees/{uid}/burnout",
    response_model=BurnoutOut
)
async def predict_burnout(uid: str):

    employee = await db["employees"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
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


    tp = await db["task_performance"].find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not tp:
        raise HTTPException(
            status_code=404,
            detail="Task performance not found"
        )


    # --------------------------------------------------
    # Extract features
    # --------------------------------------------------

    avg_hours = attendance.get(
        "avgHours",
        0
    )

    total_hours = attendance.get(
        "totalHours",
        0
    )

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

    late_arrivals = attendance.get(
        "lateArrivals",
        0
    )

    missed_checkouts = attendance.get(
        "missedCheckouts",
        0
    )

    idle_warning_days = attendance.get(
        "idleWarningDays",
        0
    )

    geo_out_of_range = attendance.get(
        "geoOutOfRangeDays",
        0
    )

    pending_tasks = tp.get(
        "pendingTasks",
        0
    )

    overdue_tasks = tp.get(
        "overdueTasks",
        0
    )


    # --------------------------------------------------
    # Prediction input
    # --------------------------------------------------

    features = np.array([[
        avg_hours,
        total_hours,
        attendance_pct,
        late_arrivals,
        missed_checkouts,
        idle_warning_days,
        geo_out_of_range,
        pending_tasks,
        overdue_tasks
    ]])


    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    prediction_encoded = model.predict(
        features
    )[0]

    probabilities = model.predict_proba(
        features
    )[0]

    risk_label = encoder.inverse_transform(
        [prediction_encoded]
    )[0]


    # --------------------------------------------------
    # Probabilities
    # --------------------------------------------------

    prob_dict = {
        encoder.classes_[i]:
        round(
            float(probabilities[i]) * 100,
            2
        )
        for i in range(len(encoder.classes_))
    }


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "uid": uid,
        "risk_level": risk_label,
        "risk_label": RISK_EMOJI.get(
            risk_label,
            risk_label
        ),
        "probabilities": prob_dict,

        "input_features": {
            "avgHours": avg_hours,
            "totalHours": total_hours,
            "attendance": attendance_pct,
            "lateArrivals": late_arrivals,
            "missedCheckouts": missed_checkouts,
            "idleWarningDays": idle_warning_days,
            "geoOutOfRange": geo_out_of_range,
            "pendingTasks": pending_tasks,
            "overdueTasks": overdue_tasks
        }
    }