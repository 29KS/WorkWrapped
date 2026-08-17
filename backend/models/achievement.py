from pydantic import BaseModel
from typing import List, Optional


class Achievement(BaseModel):
    title: str
    description: str


class LeaderboardEntry(BaseModel):
    uid: str
    name: str
    score: float
    rank: int


class AchievementOut(BaseModel):
    uid: str
    score: float
    completion_rate: float
    ontime_rate: float
    attendance_rate: float
    assessment_score: int
    achievements: List[Achievement]
    rank_in_company: int