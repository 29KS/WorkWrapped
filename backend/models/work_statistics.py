from pydantic import BaseModel
from typing import List


class ProjectStatistics(BaseModel):
    project: str
    total_tasks: int


class HoursComparison(BaseModel):
    estimated_hours: float
    actual_hours: float


class WorkStatisticsOut(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int

    completion_rate: float

    total_projects: int

    total_estimated_hours: float
    total_actual_hours: float
    average_actual_hours_per_task: float

    total_subtasks: int
    completed_subtasks: int
    subtask_completion_rate: float

    project_statistics: List[ProjectStatistics]

    hours_comparison: HoursComparison