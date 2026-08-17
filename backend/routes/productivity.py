from fastapi import APIRouter, HTTPException
from database import employee_collection
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["Productivity"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


def get_most_productive_day(tasks):
    day_counts = {}
    for task in tasks:
        if task.get("completedAt"):
            day = datetime.strptime(task["completedAt"], "%Y-%m-%d").strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
    if not day_counts:
        return None
    return max(day_counts, key=day_counts.get)


def get_longest_streak(tasks):
    dates = sorted(set(
        datetime.strptime(t["completedAt"], "%Y-%m-%d")
        for t in tasks if t.get("completedAt")
    ))
    if not dates:
        return 0
    max_streak = current = 1
    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i - 1]).days
        if diff == 1:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
    return max_streak


def get_fastest_task(tasks):
    valid = [
        t for t in tasks
        if t.get("actualHours") and t.get("project") and t.get("status") == "Done"
    ]
    if not valid:
        return None
    fastest = min(valid, key=lambda x: x["actualHours"])
    return {"title": fastest["title"], "actualHours": fastest["actualHours"]}


def get_productivity_trend(tasks):
    trend = {}
    for task in tasks:
        if task.get("completedAt"):
            date = task["completedAt"]
            trend[date] = trend.get(date, 0) + 1
    return [{"date": k, "tasks": v} for k, v in sorted(trend.items())]


def get_avg_tasks_per_day(tasks):
    dates = set(t["completedAt"] for t in tasks if t.get("completedAt"))
    total = sum(1 for t in tasks if t.get("completedAt"))
    if not dates:
        return 0
    return round(total / len(dates), 2)


def get_completion_times(tasks):
    return [
        {"title": t["title"], "actualHours": t["actualHours"]}
        for t in tasks
        if t.get("actualHours") and t.get("project") and t.get("status") == "Done"
    ]


@router.get("/{uid}/productivity")
async def get_productivity(uid: str):
    employee = await employee_collection.find_one({"uid": uid})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tp = await db["task_performance"].find_one({"uid": uid}, {"_id": 0})
    if not tp:
        raise HTTPException(status_code=404, detail="Task performance data not found")

    tasks = tp.get("tasks", [])

    return {
        "most_productive_day": get_most_productive_day(tasks),
        "longest_working_streak": get_longest_streak(tasks),
        "fastest_task": get_fastest_task(tasks),
        "average_tasks_per_day": get_avg_tasks_per_day(tasks),
        "productivity_trend": get_productivity_trend(tasks),
        "completion_time_distribution": get_completion_times(tasks)
    }