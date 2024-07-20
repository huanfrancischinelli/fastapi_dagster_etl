from dagster import repository
from jobs import etl, etl_daily
from schedules import etl_daily_schedule

@repository
def etl_repository():
    return [etl, etl_daily, etl_daily_schedule]