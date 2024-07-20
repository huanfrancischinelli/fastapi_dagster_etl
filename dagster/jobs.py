from dagster import job
from assets import etl_script, etl_daily_script
from resources import db1_session, db2_session

@job(
    resource_defs={"db1": db1_session, "db2": db2_session},
    config={
        "resources": {
            "db1": {
                "config": {
                    "database_url": "postgresql://admin:admin@db1/db1"
                },
            },
            "db2": {
                "config": {
                    "database_url": "postgresql://admin:admin@db2/db2"
                },
            },
        },
        "ops": {
            "etl_script": {
                "config": {
                    "start_date": "2024-07-17",
                    "end_date": "2024-07-18",
                    "variables": [
                        "wind_speed",
                        "power",
                        "ambient_temperature"
                    ],
                    "api_url": "http://api:5000/source/data/read",
                },
            },
        },
    }
)
def etl():
    etl_script()

@job(
    resource_defs={"db1": db1_session, "db2": db2_session},
    config={
        "resources": {
            "db1": {
                "config": {
                    "database_url": "postgresql://admin:admin@db1/db1"
                },
            },
            "db2": {
                "config": {
                    "database_url": "postgresql://admin:admin@db2/db2"
                },
            },
        },
        "ops": {
            "etl_daily_script": {
                "config": {
                    "api_url": "http://api:5000/source/data/read",
                },
            },
        },
    }
)
def etl_daily():
    etl_daily_script()