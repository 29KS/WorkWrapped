from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

router = APIRouter(tags=["Achievements"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


# ── Score formula using only JSON fields ─────────────────────
def calculate_score(tp: dict, attendance: dict, profile: dict) -> dict:
    total = tp.get("totalTasks", 1)
    done = tp.get("doneTasks", 0)
    ontime = tp.get("onTimeCompletions", 0)
    present = attendance.get("presentDays", 0)
    total_days = attendance.get("totalDays", 1)
    assessment = profile.get("assessmentScore", 0)

    completion_rate = round((done / total) * 100, 2) if total else 0
    ontime_rate = round((ontime / done) * 100, 2) if done else 0
    attendance_rate = round((present / total_days) * 100, 2) if total_days else 0

    # Weighted score out of 100
    score = round(
        (completion_rate * 0.40) +
        (ontime_rate * 0.30) +
        (attendance_rate * 0.20) +
        (assessment * 0.10),
        2
    )

    return {
        "score": score,
        "completion_rate": completion_rate,
        "ontime_rate": ontime_rate,
        "attendance_rate": attendance_rate,
        "assessment_score": assessment
    }


# ── Derive achievements from JSON fields ─────────────────────
def derive_achievements(tp: dict, attendance: dict) -> list:
    achievements = []

    # Perfect attendance
    if attendance.get("presentDays") == attendance.get("totalDays"):
        achievements.append({
            "title": "Perfect Attendance",
            "description": f"Present all {attendance['totalDays']} working days"
        })

    # Zero late completions
    if tp.get("lateCompletions") == 0 and tp.get("doneTasks", 0) > 0:
        achievements.append({
            "title": "On-Time Champion",
            "description": "Completed every task on or before deadline"
        })

    # Phase 1 complete
    for phase in tp.get("byPhase", []):
        if phase.get("total") == phase.get("done") and phase.get("done", 0) > 0:
            achievements.append({
                "title": f"Phase Complete",
                "description": f"Finished all tasks in: {phase['week']}"
            })

    # High completion rate
    total = tp.get("totalTasks", 1)
    done = tp.get("doneTasks", 0)
    if done / total >= 0.5:
        achievements.append({
            "title": "Halfway Hero",
            "description": f"Completed {done} out of {total} tasks"
        })

    # Subtask finisher
    sub_done = tp.get("subtasksDone", 0)
    sub_total = tp.get("subtasksTotal", 1)
    if sub_done / sub_total >= 0.5:
        achievements.append({
            "title": "Subtask Finisher",
            "description": f"Completed {sub_done} of {sub_total} subtasks"
        })

    return achievements


# ── GET /employees/{uid}/achievements ────────────────────────
@router.get("/employees/{uid}/achievements")
async def get_achievements(uid: str):
    profile = await db["employees"].find_one({"uid": uid}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Employee not found")

    tp = await db["task_performance"].find_one({"uid": uid}, {"_id": 0})
    if not tp:
        raise HTTPException(status_code=404, detail="Task performance data not found")

    attendance = await db["raw_attendance"].find_one({"uid": uid}, {"_id": 0})
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance data not found")

    metrics = calculate_score(tp, attendance, profile)
    achievements = derive_achievements(tp, attendance)

    # Rank in company
    all_employees = db["employees"].find({}, {"_id": 0})
    scores = []
    async for emp in all_employees:
        emp_tp = await db["task_performance"].find_one({"uid": emp["uid"]}, {"_id": 0})
        emp_att = await db["raw_attendance"].find_one({"uid": emp["uid"]}, {"_id": 0})
        if emp_tp and emp_att:
            s = calculate_score(emp_tp, emp_att, emp)
            scores.append({"uid": emp["uid"], "score": s["score"]})

    scores.sort(key=lambda x: x["score"], reverse=True)
    rank = next((i + 1 for i, s in enumerate(scores) if s["uid"] == uid), None)

    return {
        "uid": uid,
        **metrics,
        "achievements": achievements,
        "rank_in_company": rank
    }


# ── GET /leaderboard ─────────────────────────────────────────
@router.get("/leaderboard")
async def get_leaderboard():
    leaderboard = []
    async for emp in db["employees"].find({}, {"_id": 0}):
        tp = await db["task_performance"].find_one({"uid": emp["uid"]}, {"_id": 0})
        att = await db["raw_attendance"].find_one({"uid": emp["uid"]}, {"_id": 0})
        if tp and att:
            metrics = calculate_score(tp, att, emp)
            leaderboard.append({
                "uid": emp["uid"],
                "name": tp.get("internName", emp.get("email", "Unknown")),
                "score": metrics["score"],
                "completion_rate": metrics["completion_rate"],
                "ontime_rate": metrics["ontime_rate"],
                "attendance_rate": metrics["attendance_rate"],
                "assessment_score": metrics["assessment_score"]
            })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    return leaderboard