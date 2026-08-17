from pydantic import BaseModel
from typing import Dict


class BurnoutOut(BaseModel):
    uid: str
    risk_level: str
    risk_label: str
    probabilities: Dict[str, float]
    input_features: Dict[str, float]