from sqlalchemy import Column, Integer, String, Float, DateTime
from resources import Base_db2 as Base


class Signal(Base):
    __tablename__ = "signal"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
