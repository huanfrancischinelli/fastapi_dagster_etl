from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models.signal import Signal as SignalModel
from models.data import Data as DataModel
from db import get_db
import pandas as pd
import httpx


Engine_db2 = create_engine("postgresql://admin:admin@localhost:5433/db2")
Base_db2 = declarative_base()
LocalSession_db2 = sessionmaker(autocommit=False, autoflush=False, bind=Engine_db2)
Base_db2.metadata.create_all(bind=Engine_db2)


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


def etl(start_date: datetime, end_date: datetime, api_url: str, db_url: str, variables: List[str]):
    if end_date <= start_date:
        print("Invalid date.")
        raise Exception("Invalid date.")
    
    print(f"start_date: {start_date}")
    print(f"end_date: {end_date}")
    print(f"variables: {variables}")
    print(f"api_url: {api_url}")

    try:
        data = fetch_data(start_date, end_date, api_url, variables)
        print(f"Rows fetched: {len(data)}")

        if not data:
            print("No data to process.")
            return False
        
        transformed_df = transform_data(data)
        print(f"Transformed rows: {len(transformed_df)}")

        db2_session = get_db(db_url)
        signal_ids = load_signal_ids(variables, db2_session)

        created_rows = save_data(transformed_df, variables, signal_ids, db2_session)
        print(f"Rows inserted in db2.data: {created_rows}")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    API_URL = "http://localhost:5000/source/data/read"
    DB_URL = "postgresql://admin:admin@localhost:5433/db2"
    start_date = datetime(2024, 7, 20)
    end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
    variables = [
        "wind_speed",
        "power",
        # "ambient_temperature",
    ]

    etl(start_date, end_date, API_URL, DB_URL, variables)
