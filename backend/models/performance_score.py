from pydantic import BaseModel
from typing import Dict


class PerformanceScoreOut(BaseModel):
    uid: str
    predicted_score: float
    grade: str
    grade_color: str
    model_used: str
    input_features: Dict[str, float]
    feature_contribution: Dict[str, str]