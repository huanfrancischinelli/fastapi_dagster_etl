from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db2
from db2.models.signal import Signal as SignalModel
from db2.schemas.signal import Signal as SignalSchema

target_signal_routes = APIRouter()

@target_signal_routes.get("/signal/read", response_model=List[SignalSchema])
def read_target_signal(name: Optional[datetime] = None, db: Session = Depends(get_db2)):
    try:
        query = db.query(
            SignalModel.id,
            SignalModel.name,
        )

        if name:
            query = query.filter(SignalModel.name == name)

        return query.all()
    except Exception as e:
        raise e


@target_signal_routes.get("/signal/reset")
def reset_target_signal(db: Session = Depends(get_db2)):
    print("Resetting target signal table...")
    try:
        num_deleted = db.query(SignalModel).delete()
        db.commit()
        return {"message": f"{num_deleted} records deleted."}
    except Exception as e:
        db.rollback()
        raise e

