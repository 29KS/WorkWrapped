from pydantic import BaseModel
from typing import List


class WeeklyPerformance(BaseModel):
    week: str
    completed_tasks: int


class PerformanceMetrics(BaseModel):
    on_time_tasks: int
    delayed_tasks: int
    on_time_delivery_percentage: float
    overall_performance_score: float


class PerformanceOut(BaseModel):
    tasks_completed_before_deadline: int
    delayed_tasks: int
    on_time_delivery_percentage: float

    weekly_consistency: List[WeeklyPerformance]

    overall_performance_score: float

    performance_metrics: PerformanceMetrics