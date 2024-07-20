from dagster import schedule

@schedule(cron_schedule="0 0 * * *", job_name="etl_daily", execution_timezone="America/Sao_Paulo")
def etl_daily_schedule():
    return {}
