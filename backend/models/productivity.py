from pydantic import BaseModel
from typing import Optional, List


class TaskTrend(BaseModel):
    date: str
    tasks: int


class FastestTask(BaseModel):
    title: str
    actualHours: float


class CompletionTime(BaseModel):
    title: str
    actualHours: float


class ProductivityOut(BaseModel):
    most_productive_day: Optional[str] = None
    longest_working_streak: int
    fastest_task: Optional[FastestTask] = None
    average_tasks_per_day: float
    productivity_trend: List[TaskTrend]
    completion_time_distribution: List[CompletionTime]