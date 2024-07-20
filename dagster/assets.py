from dagster import asset, Field
from datetime import datetime, timedelta
import pandas as pd
import httpx
from db2.models.signal import Signal as SignalModel
from db2.models.data import Data as DataModel
from typing import Dict, List, Optional


def fetch_data(start_date: datetime, end_date: datetime, api_url: str, variables: Optional[List[str]] = list()) -> List[Dict]:
    """Fetch data from the source."""
    response = httpx.get(
        api_url,
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "variables": variables,
        }
    )
    response.raise_for_status()
    return response.json()


def transform_data(data: List[Dict]) -> pd.DataFrame:
    """Transform the fetched data."""
    df = pd.DataFrame(data).dropna(axis=1, how='all')
    df.set_index('timestamp', inplace=True)
    df.index = pd.to_datetime(df.index)
    agg_df = df.resample('10min').agg(['mean', 'min', 'max', 'std']).dropna()
    agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
    return agg_df


def load_signal_ids(variables: List[str], db) -> int:
    """Load Signal ID's from Signal table."""
    signal_ids = {}
    for var in variables:
        curr = db.query(SignalModel).filter(SignalModel.name == var).first()
        if not curr:
            curr = SignalModel(name=var)
            db.add(curr)
            db.commit()
            db.refresh(curr)
        signal_ids[var] = curr.id
    return signal_ids


def save_data(df: pd.DataFrame, variables: List[str], signal_ids: Dict[str, str], db) -> int:
    """Save transformed data into Data table."""
    created = 0
    for timestamp, row in df.iterrows():
        for var in variables:
            new_data = DataModel(
                timestamp=timestamp,
                signal_id=signal_ids[var],
                mean_value=float(row[f'{var}_mean']),
                min_value=float(row[f'{var}_min']),
                max_value=float(row[f'{var}_max']),
                std_value=float(row[f'{var}_std'])
            )
            db.add(new_data)
            created += 1
    db.commit()
    return created


@asset(
    required_resource_keys={"db2"},
    config_schema={
        "api_url": Field(str, is_required=True, description="API url"),
        "start_date": Field(str, is_required=True, description="Start Date of the request"),
        "end_date": Field(str, is_required=True, description="End Date of the request"),
        "variables": Field(list, is_required=True, description="List of variables to be processed"),
    },
)
def etl_script(context):
    start_date = datetime.fromisoformat(context.op_config["start_date"])
    end_date = datetime.fromisoformat(context.op_config["end_date"])
    
    if end_date <= start_date:
        context.log.error("Invalid date.")
        raise Exception("Invalid date.")
    
    variables = context.op_config["variables"]
    api_url = context.op_config["api_url"]

    context.log.debug(f"start_date: {start_date}")
    context.log.debug(f"end_date: {end_date}")
    context.log.debug(f"variables: {variables}")
    context.log.debug(f"api_url: {api_url}")

    try:
        data = fetch_data(start_date, end_date, api_url, variables)
        context.log.info(f"Rows fetched: {len(data)}")

        if not data:
            context.log.warning("No data to process.")
            return False
        
        transformed_df = transform_data(data)
        context.log.info(f"Transformed rows: {len(transformed_df)}")

        db2_session = context.resources.db2
        signal_ids = load_signal_ids(variables, db2_session)

        created_rows = save_data(transformed_df, variables, signal_ids, db2_session)
        context.log.info(f"Rows inserted in db2.data: {created_rows}")
        
        return True

    except httpx.RequestError as e:
        context.log.error(f"Request error occurred: {e}")
        return False
    except Exception as e:
        context.log.error(f"An error occurred: {e}")
        return False


@asset(
    required_resource_keys={"db2"},
    config_schema={
        "api_url": Field(str, is_required=True, description="API url"),
    },
)
def etl_daily_script(context):
    curr_date = datetime.now()
    start_date = datetime(curr_date.year, curr_date.month, curr_date.day) - timedelta(days=1)
    end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
    variables = [
        "wind_speed",
        "power",
        "ambient_temperature",
    ]
    api_url = context.op_config["api_url"]

    context.log.debug(f"start_date: {start_date}")
    context.log.debug(f"end_date: {end_date}")
    context.log.debug(f"variables: {variables}")
    context.log.debug(f"api_url: {api_url}")

    try:
        data = fetch_data(start_date, end_date, api_url)
        context.log.info(f"Rows fetched: {len(data)}")

        if not data:
            context.log.warning("No data to process.")
            return False
        
        transformed_df = transform_data(data)
        context.log.info(f"Transformed rows: {len(transformed_df)}")

        db2_session = context.resources.db2
        signal_ids = load_signal_ids(variables, db2_session)

        created_rows = save_data(transformed_df, variables, signal_ids, db2_session)
        context.log.info(f"Rows inserted in db2.data: {created_rows}")
        
        return True

    except httpx.RequestError as e:
        context.log.error(f"Request error occurred: {e}")
        return False
    except Exception as e:
        context.log.error(f"An error occurred: {e}")
        return False
