from fastapi import FastAPI
from contextlib import asynccontextmanager
from db1.routes.source_data_routes import source_data_routes
from db2.routes.target_data_routes import target_data_routes
from db2.routes.target_signal_routes import target_signal_routes
from routes.main_routes import main_routes
from db import Base_db1, Base_db2, Engine_db1, Engine_db2
from scripts import randomize_source_data
from datetime import datetime, timedelta

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Recreating databases...")
    Base_db1.metadata.drop_all(bind=Engine_db1)
    Base_db2.metadata.drop_all(bind=Engine_db2)
    Base_db1.metadata.create_all(bind=Engine_db1)
    Base_db2.metadata.create_all(bind=Engine_db2)
    randomize_source_data(
        start_date=datetime.now() - timedelta(days=5),
        period=10,
        minutes=1
    )
    yield
    print("Exiting...")

app = FastAPI(lifespan=lifespan)


app.include_router(main_routes, prefix="", tags=["main"])

app.include_router(source_data_routes, prefix="/source", tags=["source"])
app.include_router(target_data_routes, prefix="/target", tags=["target_data"])
app.include_router(target_signal_routes, prefix="/target", tags=["target_signal"])
