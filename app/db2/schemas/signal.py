from datetime import datetime
from pydantic import BaseModel

class Signal(BaseModel):
    name: str

    class Config:
        from_attributes = True
