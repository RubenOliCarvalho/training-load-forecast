import os
from datetime import date
from dotenv import load_dotenv
import requests
import psycopg2
import psycopg2.extras

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Deliberately far back - captures your full history regardless of how far
# it actually goes. The API just returns whatever exists in this range,
# so there's no harm in requesting more than necessary.
OLDEST_DATE = "2000-01-01"


def fetch_activities():
    response = requests.get(
        "https://intervals.icu/api/v1/athlete/0/activities",
        params={"oldest": OLDEST_DATE, "newest": date.today().isoformat()},
        auth=("API_KEY", API_KEY),
    )
    response.raise_for_status()
    return response.json()


def upsert_activities(activities):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    upsert_sql = """
        INSERT INTO staging.intervals_activities_raw (
            activity_id, athlete_id, name, activity_type, source, trainer,
            start_date_local, start_date_utc,
            moving_time_secs, elapsed_time_secs,
            training_load, ctl, atl, trimp,
            avg_heartrate, max_heartrate, efficiency_factor, decoupling, intensity,
            avg_watts, weighted_avg_watts, ftp_at_activity,
            distance_m, elevation_gain_m, avg_speed_mps, avg_cadence,
            calories, avg_temp_c, min_temp_c, max_temp_c,
            raw_json
        )
        VALUES (
            %(id)s, %(athlete_id)s, %(name)s, %(type)s, %(source)s, %(trainer)s,
            %(start_local)s, %(start_utc)s,
            %(moving)s, %(elapsed)s,
            %(load)s, %(ctl)s, %(atl)s, %(trimp)s,
            %(avg_hr)s, %(max_hr)s, %(ef)s, %(decoupling)s, %(intensity)s,
            %(avg_watts)s, %(weighted_watts)s, %(ftp)s,
            %(distance)s, %(elev_gain)s, %(avg_speed)s, %(avg_cadence)s,
            %(calories)s, %(avg_temp)s, %(min_temp)s, %(max_temp)s,
            %(raw)s
        )
        ON CONFLICT (activity_id) DO UPDATE SET
            name = EXCLUDED.name,
            activity_type = EXCLUDED.activity_type,
            source = EXCLUDED.source,
            trainer = EXCLUDED.trainer,
            start_date_local = EXCLUDED.start_date_local,
            start_date_utc = EXCLUDED.start_date_utc,
            moving_time_secs = EXCLUDED.moving_time_secs,
            elapsed_time_secs = EXCLUDED.elapsed_time_secs,
            training_load = EXCLUDED.training_load,
            ctl = EXCLUDED.ctl,
            atl = EXCLUDED.atl,
            trimp = EXCLUDED.trimp,
            avg_heartrate = EXCLUDED.avg_heartrate,
            max_heartrate = EXCLUDED.max_heartrate,
            efficiency_factor = EXCLUDED.efficiency_factor,
            decoupling = EXCLUDED.decoupling,
            intensity = EXCLUDED.intensity,
            avg_watts = EXCLUDED.avg_watts,
            weighted_avg_watts = EXCLUDED.weighted_avg_watts,
            ftp_at_activity = EXCLUDED.ftp_at_activity,
            distance_m = EXCLUDED.distance_m,
            elevation_gain_m = EXCLUDED.elevation_gain_m,
            avg_speed_mps = EXCLUDED.avg_speed_mps,
            avg_cadence = EXCLUDED.avg_cadence,
            calories = EXCLUDED.calories,
            avg_temp_c = EXCLUDED.avg_temp_c,
            min_temp_c = EXCLUDED.min_temp_c,
            max_temp_c = EXCLUDED.max_temp_c,
            raw_json = EXCLUDED.raw_json,
            pulled_at = now();
    """

    for a in activities:
        cur.execute(upsert_sql, {
            "id": a["id"],
            "athlete_id": a.get("icu_athlete_id"),
            "name": a.get("name"),
            "type": a.get("type"),
            "source": a.get("source"),
            "trainer": a.get("trainer"),
            "start_local": a.get("start_date_local"),
            "start_utc": a.get("start_date"),
            "moving": a.get("moving_time"),
            "elapsed": a.get("elapsed_time"),
            "load": a.get("icu_training_load"),
            "ctl": a.get("icu_ctl"),
            "atl": a.get("icu_atl"),
            "trimp": a.get("trimp"),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "ef": a.get("icu_efficiency_factor"),
            "decoupling": a.get("decoupling"),
            "intensity": a.get("icu_intensity"),
            "avg_watts": a.get("icu_average_watts"),
            "weighted_watts": a.get("icu_weighted_avg_watts"),
            "ftp": a.get("icu_ftp"),
            "distance": a.get("icu_distance"),
            "elev_gain": a.get("total_elevation_gain"),
            "avg_speed": a.get("average_speed"),
            "avg_cadence": a.get("average_cadence"),
            "calories": a.get("calories"),
            "avg_temp": a.get("average_temp"),
            "min_temp": a.get("min_temp"),
            "max_temp": a.get("max_temp"),
            "raw": psycopg2.extras.Json(a),
        })

    conn.commit()
    print(f"Upserted {len(activities)} activities.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    activities = fetch_activities()
    upsert_activities(activities)