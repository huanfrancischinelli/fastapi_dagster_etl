from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base_db2 = declarative_base()

def get_db(db_url: str):
    Engine = create_engine(db_url)
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    db = LocalSession()
    try:
        return db
    finally:
        db.close_all()
