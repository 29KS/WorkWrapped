from pydantic import BaseModel
from typing import Optional, List


class PriorProject(BaseModel):
    title: str
    description: Optional[str] = None


class CurrentProject(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[str] = None


class TaskProjectStat(BaseModel):
    project: str
    totalTasks: int
    doneTasks: int
    actualHours: float
    estHours: float


class ProjectOut(BaseModel):
    total_projects: int
    biggest_project: Optional[str] = None
    highest_contribution: Optional[str] = None
    most_active_project: Optional[str] = None
    completed_projects: List[str]
    prior_projects: List[PriorProject]
    current_projects: List[CurrentProject]
    task_project_stats: List[TaskProjectStat]