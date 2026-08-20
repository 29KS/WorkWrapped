from fastapi import APIRouter, HTTPException
from backend.database import employee_collection
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import MONGO_URI, DB_NAME

router = APIRouter(prefix="/employees", tags=["Work Statistics"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


def get_completion_rate(done, total):
    if total == 0:
        return 0
    return round((done / total) * 100, 2)


def get_average_actual_hours(total_actual, completed):
    if completed == 0:
        return 0
    return round(total_actual / completed, 2)


def get_subtask_completion(done, total):
    if total == 0:
        return 0
    return round((done / total) * 100, 2)


def get_project_statistics(tasks):
    project_counts = {}

    for task in tasks:
        project = task.get("project")

        if not project:      # Skip None or empty values
            continue

        project_counts[project] = project_counts.get(project, 0) + 1

    return [
        {"project": project, "tasks": count}
        for project, count in sorted(project_counts.items())
    ]


@router.get("/{uid}/work-statistics")
async def get_work_statistics(uid: str):

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
            detail="Task performance data not found"
        )

    tasks = tp.get("tasks", [])

    total_tasks = tp.get("doneTasks", 0) + tp.get("pendingTasks", 0)

    completed_tasks = tp.get("doneTasks", 0)
    pending_tasks = tp.get("pendingTasks", 0)
    overdue_tasks = tp.get("overdueTasks", 0)

    completion_rate = get_completion_rate(
        completed_tasks,
        total_tasks
    )

    total_projects = len(
        set(
            task.get("project")
            for task in tasks
            if task.get("project")
        )
    )

    total_estimated_hours = tp.get("totalEstimatedHours", 0)
    total_actual_hours = tp.get("totalActualHours", 0)

    average_actual_hours = get_average_actual_hours(
        total_actual_hours,
        completed_tasks
    )

    total_subtasks = tp.get("subtasksTotal", 0)
    completed_subtasks = tp.get("subtasksDone", 0)

    subtask_completion = get_subtask_completion(
        completed_subtasks,
        total_subtasks
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,

        "completion_rate": completion_rate,

        "total_projects": total_projects,

        "total_estimated_hours": total_estimated_hours,
        "total_actual_hours": total_actual_hours,
        "average_actual_hours_per_task": average_actual_hours,

        "total_subtasks": total_subtasks,
        "completed_subtasks": completed_subtasks,
        "subtask_completion_rate": subtask_completion,

        "project_statistics": get_project_statistics(tasks),

        "hours_comparison": {
            "estimated_hours": total_estimated_hours,
            "actual_hours": total_actual_hours
        }
    }