from datetime import datetime
from pydantic import BaseModel

class Data(BaseModel):
    timestamp: datetime
    signal_id: int
    mean_value: float
    min_value: float
    max_value: float
    std_value: float

    class Config:
        from_attributes = True
