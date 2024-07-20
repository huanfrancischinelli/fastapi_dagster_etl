from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Data(BaseModel):
    timestamp: datetime
    wind_speed: Optional[float] = None
    power: Optional[float] = None
    ambient_temperature: Optional[float] = None

    class Config:
        from_attributes = True
