from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DB_NAME
from backend.services.gemini_service import generate_employee_summary
import pickle
import numpy as np

router = APIRouter(tags=["Wrapped"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# load ML models
try:
    with open("ml/burnout_model.pkl", "rb") as f:
        burnout_saved = pickle.load(f)
        burnout_model   = burnout_saved["model"]
        burnout_encoder = burnout_saved["encoder"]
except Exception:
    burnout_model = None

try:
    with open("ml/score/score_model.pkl", "rb") as f:
        score_saved  = pickle.load(f)
        score_model  = score_saved["model"]
except Exception:
    score_model = None

try:
    with open("ml/personality/personality_model.pkl", "rb") as f:
        pers_saved    = pickle.load(f)
        pers_model    = pers_saved["model"]
        pers_encoder  = pers_saved["encoder"]
except Exception:
    pers_model = None


def get_grade(score: float) -> str:
    if score >= 90: return "A+"
    elif score >= 80: return "A"
    elif score >= 70: return "B"
    elif score >= 60: return "C"
    else: return "D"


@router.get("/employees/{uid}/wrapped")
async def get_wrapped(uid: str):
    # fetch all collections
    emp = await db["employees"].find_one({"uid": uid}, {"_id": 0})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    tp  = await db["task_performance"].find_one({"uid": uid}, {"_id": 0})
    att = await db["raw_attendance"].find_one({"uid": uid}, {"_id": 0})

    if not tp or not att:
        raise HTTPException(status_code=404, detail="Data not found")

    # ── derived fields ────────────────────────────────────────
    tasks     = tp.get("tasks", [])
    done_list = [t for t in tasks if t.get("status") == "Done" and t.get("actualHours")]

    present    = att.get("presentDays", 0)
    total_days = att.get("totalDays", 1)
    att_pct    = round((present / total_days) * 100, 2)

    done       = tp.get("doneTasks", 0)
    total      = tp.get("totalTasks", 1)
    comp_rate  = round((done / total) * 100, 2)

    ontime     = tp.get("onTimeCompletions", 0)
    ontime_pct = round((ontime / done) * 100, 2) if done else 0

    projects   = len(set(t.get("project") for t in tasks if t.get("project")))
    avg_hrs    = att.get("avgHours", 0)
    late       = att.get("lateArrivals", 0)
    missed     = att.get("missedCheckouts", 0)
    idle       = att.get("idleWarningDays", 0)
    geo        = att.get("geoOutOfRangeDays", 0)
    pending    = tp.get("pendingTasks", 0)
    overdue    = tp.get("overdueTasks", 0)
    total_hrs  = att.get("totalHours", 0)

    # ── burnout prediction ────────────────────────────────────
    burnout_risk = "N/A"
    if burnout_model:
        b_feat = np.array([[
            avg_hrs, total_hrs, att_pct,
            late, missed, idle, geo, pending, overdue
        ]])
        b_pred       = burnout_model.predict(b_feat)[0]
        burnout_risk = burnout_encoder.inverse_transform([b_pred])[0]

    # ── performance score prediction ──────────────────────────
    perf_score = "N/A"
    perf_grade = "N/A"
    if score_model:
        s_feat     = np.array([[att_pct, comp_rate, projects, avg_hrs, late]])
        perf_score = round(float(np.clip(score_model.predict(s_feat)[0], 0, 100)), 2)
        perf_grade = get_grade(perf_score)

    # ── personality prediction ────────────────────────────────
    personality = "N/A"
    personality_emoji = "⭐"
    if pers_model:
        avg_comp = round(
            sum(t["actualHours"] for t in done_list) / len(done_list), 2
        ) if done_list else 0
        p_feat      = np.array([[done, avg_comp, att_pct, projects, avg_hrs, ontime_pct]])
        p_pred      = pers_model.predict(p_feat)[0]
        personality = pers_encoder.inverse_transform([p_pred])[0]

        emoji_map = {
            "Speedster":            "🚀",
            "Consistency Champion": "🔥",
            "Problem Solver":       "💡",
            "Multitasker":          "🎯",
            "Planner":              "📈",
            "Balanced Performer":   "🤝"
        }
        personality_emoji = emoji_map.get(personality, "⭐")

    # ── build employee dict for Gemini ────────────────────────
    employee_data = {
        "name":               tp.get("internName", emp.get("email", "").split("@")[0]),
        "department":         emp.get("department"),
        "position":           emp.get("position"),
        "role":               emp.get("role"),
        "joinDate":           emp.get("joinDate"),
        "presentDays":        present,
        "leaveDays":          att.get("leaveDays", 0),
        "lateArrivals":       late,
        "avgHours":           avg_hrs,
        "doneTasks":          done,
        "pendingTasks":       pending,
        "overdueTasks":       overdue,
        "onTimeCompletions":  ontime,
        "totalEstimatedHours": tp.get("totalEstimatedHours", 0),
        "totalActualHours":   tp.get("totalActualHours", 0)
    }

    prediction_data = {
        "burnoutRisk":       burnout_risk,
        "workPersonality":   f"{personality_emoji} {personality}",
        "performanceScore":  perf_score,
        "performanceGrade":  perf_grade
    }

    # ── call Gemini ───────────────────────────────────────────
    summary = generate_employee_summary(employee_data, prediction_data)

    return {
        "uid":              uid,
        "name":             employee_data["name"],
        "department":       emp.get("department"),
        "position":         emp.get("position"),
        "joinDate":         emp.get("joinDate"),
        "summary":          summary,
        "stats": {
            "tasks_completed":   done,
            "pending_tasks":     pending,
            "attendance_pct":    att_pct,
            "ontime_pct":        ontime_pct,
            "avg_hours":         avg_hrs,
            "total_hours":       total_hrs,
            "projects":          projects,
            "completion_rate":   comp_rate
        },
        "predictions": {
            "burnout_risk":       burnout_risk,
            "personality":        personality,
            "personality_emoji":  personality_emoji,
            "performance_score":  perf_score,
            "performance_grade":  perf_grade
        },
        "phases": tp.get("byPhase", [])
    }