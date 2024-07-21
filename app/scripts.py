
from fastapi import Depends
from datetime import datetime, timedelta
from db1.models.data import Data as DataModel
from sqlalchemy.orm import Session
from db import LocalSession_db1
from typing import Optional
import random

def randomize_source_data(start_date: datetime, end_date: Optional[datetime] = None, period: Optional[int] = None, minutes: int = None,  db: Session = LocalSession_db1()):
    if not end_date and not period:
        raise Exception("One of the following variables must be present: 'end_date', 'period'")
    if not end_date:
        end_date = start_date + timedelta(days=period)
    if end_date <= start_date:
        raise Exception("Invalid date to randomize data.")
    start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    print("Generating random source database with these parameters:")
    print(f"     - start_date: {start_date}")
    print(f"     - end_date: {end_date}")
    print(f"     - period: {period}")
    print(f"     - minutes: {minutes}")
    num_created = 0
    current_time = start_date
    while current_time <= end_date:
        data_entry = DataModel(
            timestamp=current_time,
            wind_speed=random.uniform(0, 30),
            power=random.uniform(0, 100),
            ambient_temperature=random.uniform(-10, 40)
        )
        db.add(data_entry)
        num_created += 1
        if minutes:
            current_time += timedelta(minutes=minutes)
        else:
            current_time += timedelta(minutes=int(random.uniform(1, 10)))
    db.commit()
    print(f"{num_created} records randomly created.")
    return num_created