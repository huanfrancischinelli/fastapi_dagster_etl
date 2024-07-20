from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Engine_db1 = create_engine(os.environ.get('DB1_URL'))
Base_db1 = declarative_base()
LocalSession_db1 = sessionmaker(autocommit=False, autoflush=False, bind=Engine_db1)

Engine_db2 = create_engine(os.environ.get('DB2_URL'))
Base_db2 = declarative_base()
LocalSession_db2 = sessionmaker(autocommit=False, autoflush=False, bind=Engine_db2)


def get_db1():
    db = LocalSession_db1()
    try:
        yield db
    finally:
        db.close_all()


def get_db2():
    db = LocalSession_db2()
    try:
        yield db
    finally:
        db.close_all()
