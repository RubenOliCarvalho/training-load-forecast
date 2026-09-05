import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "data"

TABLES = {
    "daily": "select * from analytics.mart_daily_training order by calendar_date",
    "weekly": "select * from analytics.mart_weekly_training order by week_start",
    "monthly": "select * from analytics.mart_monthly_training order by month",
    "activities": "select * from analytics.mart_activity_diary order by start_date_local desc",
}


def export_table(engine, name, query):
    df = pd.read_sql(query, engine)
    output_path = OUTPUT_DIR / f"{name}.json"
    df.to_json(output_path, orient="records", date_format="iso", indent=2)
    print(f"Wrote {len(df)} rows to {output_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DB_URL)
    for name, query in TABLES.items():
        export_table(engine, name, query)


if __name__ == "__main__":
    main()