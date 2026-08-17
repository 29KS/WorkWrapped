from pydantic import BaseModel
from typing import Dict


class PersonalityOut(BaseModel):
    uid: str
    personality: str
    emoji: str
    description: str
    probabilities: Dict[str, float]
    input_features: Dict[str, float]