from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db2
from db2.models.data import Data as DataModel
from db2.schemas.data import Data as DataSchema
from db2.models.signal import Signal as SignalModel

target_data_routes = APIRouter()

@target_data_routes.get("/data/read", response_model=List[DataSchema])
def read_target_data(timestamp: Optional[datetime] = None, signal_id: Optional[int] = None, name: Optional[str] = None, db: Session = Depends(get_db2)):
    try:
        query = db.query(
            DataModel.timestamp,
            DataModel.signal_id,
            SignalModel.name,
            DataModel.mean_value,
            DataModel.min_value,
            DataModel.max_value,
            DataModel.std_value,
        ).join(SignalModel, DataModel.signal_id == SignalModel.id)

        if timestamp:
            query = query.filter(DataModel.timestamp == timestamp)
        if signal_id:
            query = query.filter(DataModel.signal_id == signal_id)
        if name:
            query = query.filter(SignalModel.name == name)
        return query.all()
    except Exception as e:
        raise e


@target_data_routes.get("/data/reset")
def reset_target_data(db: Session = Depends(get_db2)):
    print("Resetting target data table...")
    try:
        num_deleted = db.query(DataModel).delete()
        db.commit()
        return {"message": f"{num_deleted} records deleted."}
    except Exception as e:
        db.rollback()
        raise e

