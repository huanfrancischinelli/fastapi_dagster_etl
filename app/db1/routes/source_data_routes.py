from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db1
from db1.models.data import Data as DataModel
from db1.schemas.data import Data as DataSchema
import random

source_data_routes = APIRouter()

@source_data_routes.get("/data/read", response_model=List[DataSchema])
def read_source_data(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, variables: Optional[List[str]] = Query(None), db: Session = Depends(get_db1)):
    if not start_date or not end_date:
        curr_date = datetime.now()
        start_date = datetime(curr_date.year, curr_date.month, curr_date.day)
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
    
    try:
        query = db.query(DataModel).filter(DataModel.timestamp >= start_date, DataModel.timestamp <= end_date)
        if variables:
            column_err = []
            columns = [DataModel.timestamp]
            for var in variables:
                if hasattr(DataModel, var):
                    columns.append(getattr(DataModel, var))
                else:
                    column_err.append(var)
            query = query.with_entities(*columns)
            if column_err:
                column_err = ', '.join(f"'{column}'" for column in column_err)
                raise HTTPException(
                    status_code=422,
                    detail={"message": f"The following columns are not present in the table: {column_err}"}
                )
        return query.all()
    except Exception as e:
        raise e


@source_data_routes.get("/data/reset")
def reset_source_data(db: Session = Depends(get_db1)):
    print("Resetting source database...")
    try:
        num_deleted = db.query(DataModel).delete()
        db.commit()
        return {"message": f"{num_deleted} records deleted."}
    except Exception as e:
        db.rollback()
        raise e


@source_data_routes.get("/data/randomize")
def random_source_data(start_date: datetime, end_date: Optional[datetime] = None, period: Optional[int] = None, minutes: Optional[int] = None, db: Session = Depends(get_db1)):
    print("Generating random source database...")
    try:
        if not end_date and not period:
            raise HTTPException(status_code=422, detail={"message": "One of the following variables must be present: 'end_date', 'period'"})
        if not end_date:
            end_date = start_date + timedelta(days=period)

        num_created = 0
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
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
        return {"message": f"{num_created} records randomly created."}
    except Exception as e:
        db.rollback()
        raise e