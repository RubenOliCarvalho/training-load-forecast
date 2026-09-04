import os
from datetime import date, timedelta
from dotenv import load_dotenv
import requests
import psycopg2

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

LOOKBACK_DAYS = 90  # re-fetch a rolling window; upsert handles overlap safely


def fetch_activities():
    newest = date.today()
    oldest = newest - timedelta(days=LOOKBACK_DAYS)
    response = requests.get(
        "https://intervals.icu/api/v1/athlete/0/activities",
        params={"oldest": oldest.isoformat(), "newest": newest.isoformat()},
        auth=("API_KEY", API_KEY),
    )
    response.raise_for_status()  # fail loudly if the API call itself failed
    return response.json()


def upsert_activities(activities):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    upsert_sql = """
        INSERT INTO staging.intervals_activities_raw (
            activity_id, athlete_id, start_date_local, start_date_utc,
            activity_type, source, training_load, ctl, atl,
            moving_time_secs, elapsed_time_secs, avg_heartrate,
            max_heartrate, calories, raw_json
        )
        VALUES (
            %(id)s, %(athlete_id)s, %(start_local)s, %(start_utc)s,
            %(type)s, %(source)s, %(load)s, %(ctl)s, %(atl)s,
            %(moving)s, %(elapsed)s, %(avg_hr)s, %(max_hr)s,
            %(calories)s, %(raw)s
        )
        ON CONFLICT (activity_id) DO UPDATE SET
            training_load = EXCLUDED.training_load,
            ctl = EXCLUDED.ctl,
            atl = EXCLUDED.atl,
            raw_json = EXCLUDED.raw_json,
            pulled_at = now();
    """

    for a in activities:
        cur.execute(upsert_sql, {
            "id": a["id"],
            "athlete_id": a.get("icu_athlete_id"),
            "start_local": a.get("start_date_local"),
            "start_utc": a.get("start_date"),
            "type": a.get("type"),
            "source": a.get("source"),
            "load": a.get("icu_training_load"),
            "ctl": a.get("icu_ctl"),
            "atl": a.get("icu_atl"),
            "moving": a.get("moving_time"),
            "elapsed": a.get("elapsed_time"),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "calories": a.get("calories"),
            "raw": psycopg2.extras.Json(a),
        })

    conn.commit()
    print(f"Upserted {len(activities)} activities.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    import psycopg2.extras
    activities = fetch_activities()
    upsert_activities(activities)