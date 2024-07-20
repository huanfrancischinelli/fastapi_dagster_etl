from sqlalchemy import Column, Integer, String, Float, DateTime
from resources import Base_db2 as Base


class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    signal_id = Column(Integer, index=True)
    mean_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    std_value = Column(Float)
