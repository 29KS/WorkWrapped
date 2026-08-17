from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

router = APIRouter(tags=["Projects"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


def get_task_project_stats(tasks: list) -> list:
    stats = {}
    for task in tasks:
        proj = task.get("project")
        if not proj:
            continue
        if proj not in stats:
            stats[proj] = {
                "project": proj,
                "totalTasks": 0,
                "doneTasks": 0,
                "actualHours": 0.0,
                "estHours": 0.0
            }
        stats[proj]["totalTasks"] += 1
        if task.get("status") == "Done":
            stats[proj]["doneTasks"] += 1
        stats[proj]["actualHours"] += task.get("actualHours") or 0
        stats[proj]["estHours"] += task.get("estHours") or 0

    for k in stats:
        stats[k]["actualHours"] = round(stats[k]["actualHours"], 2)
        stats[k]["estHours"] = round(stats[k]["estHours"], 2)

    return list(stats.values())


@router.get("/employees/{uid}/projects")
async def get_projects(uid: str):
    employee = await db["employees"].find_one({"uid": uid}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tp = await db["task_performance"].find_one({"uid": uid}, {"_id": 0})
    if not tp:
        raise HTTPException(status_code=404, detail="Task performance not found")

    proj_doc = await db["projects"].find_one({"uid": uid}, {"_id": 0})
    if not proj_doc:
        raise HTTPException(status_code=404, detail="Projects data not found")

    tasks = tp.get("tasks", [])
    task_stats = get_task_project_stats(tasks)
    prior_projects = proj_doc.get("priorProjects", [])

    biggest = max(task_stats, key=lambda x: x["estHours"], default=None)
    contribution = max(task_stats, key=lambda x: x["actualHours"], default=None)
    most_active = max(task_stats, key=lambda x: x["totalTasks"], default=None)

    completed = [
        s["project"] for s in task_stats
        if s["totalTasks"] > 0 and s["doneTasks"] == s["totalTasks"]
    ]

    task_project_names = set(s["project"] for s in task_stats)
    prior_names = set(p["title"] for p in prior_projects)
    total = len(task_project_names | prior_names)

    return {
        "total_projects": total,
        "biggest_project": biggest["project"] if biggest else None,
        "highest_contribution": contribution["project"] if contribution else None,
        "most_active_project": most_active["project"] if most_active else None,
        "completed_projects": completed,
        "prior_projects": prior_projects,
        "task_project_stats": task_stats
    }