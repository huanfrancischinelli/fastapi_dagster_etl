from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dagster import resource

Base_db1 = declarative_base()
Base_db2 = declarative_base()

@resource(config_schema={"database_url": str})
def db1_session(init_context):
    engine = create_engine(init_context.resource_config["database_url"])
    Session = sessionmaker(bind=engine)
    return Session()


@resource(config_schema={"database_url": str})
def db2_session(init_context):
    engine = create_engine(init_context.resource_config["database_url"])
    Session = sessionmaker(bind=engine)
    return Session()
