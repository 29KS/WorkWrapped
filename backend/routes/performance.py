from fastapi import APIRouter, HTTPException
from backend.database import employee_collection
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DB_NAME

router = APIRouter(prefix="/employees", tags=["Performance"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


def calculate_on_time_percentage(on_time, delayed):
    total = on_time + delayed
    if total == 0:
        return 0
    return round((on_time / total) * 100, 2)


def calculate_overall_score(tp):
    score = 0

    completion_rate = (
        tp.get("doneTasks", 0)
        / max(tp.get("doneTasks", 0) + tp.get("pendingTasks", 0), 1)
    ) * 100

    on_time_rate = calculate_on_time_percentage(
        tp.get("onTimeCompletions", 0),
        tp.get("lateCompletions", 0)
    )

    subtask_rate = (
        tp.get("subtasksDone", 0)
        / max(tp.get("subtasksTotal", 1), 1)
    ) * 100

    score = (
        completion_rate * 0.4 +
        on_time_rate * 0.4 +
        subtask_rate * 0.2
    )

    return round(score, 2)


def get_weekly_consistency(tp):
    weeks = tp.get("byPhase", [])

    result = []

    for week in weeks:
        result.append({
            "week": week.get("week", "Unknown"),
            "completed_tasks": week.get("done", 0)
        })

    return result


@router.get("/{uid}/performance")
async def get_performance(uid: str):

    employee = await employee_collection.find_one({"uid": uid})

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
            detail="Performance data not found"
        )

    on_time = tp.get("onTimeCompletions", 0)
    delayed = tp.get("lateCompletions", 0)

    on_time_percentage = calculate_on_time_percentage(
        on_time,
        delayed
    )

    overall_score = calculate_overall_score(tp)

    return {

        "tasks_completed_before_deadline": on_time,

        "delayed_tasks": delayed,

        "on_time_delivery_percentage": on_time_percentage,

        "weekly_consistency": get_weekly_consistency(tp),

        "overall_performance_score": overall_score,

        "performance_metrics": {

            "on_time_tasks": on_time,

            "delayed_tasks": delayed,

            "on_time_delivery_percentage": on_time_percentage,

            "overall_performance_score": overall_score

        }

    }
