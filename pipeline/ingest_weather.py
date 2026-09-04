import os
from datetime import date, timedelta
from dotenv import load_dotenv
import requests
import psycopg2
import psycopg2.extras

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

LATITUDE = -33.46
LONGITUDE = 18.73
LOOKBACK_DAYS = 90


def fetch_weather():
    end = date.today()
    start = end - timedelta(days=LOOKBACK_DAYS)
    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "Africa/Johannesburg",
        },
    )
    response.raise_for_status()
    return response.json()


def upsert_weather(data):
    daily = data["daily"]
    dates = daily["time"]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    upsert_sql = """
        INSERT INTO staging.weather_daily (
            weather_date, latitude, longitude,
            temp_max_c, temp_min_c, precipitation_mm, wind_speed_max_kmh, raw_json
        )
        VALUES (
            %(date)s, %(lat)s, %(lon)s,
            %(temp_max)s, %(temp_min)s, %(precip)s, %(wind_max)s, %(raw)s
        )
        ON CONFLICT (weather_date) DO UPDATE SET
            temp_max_c = EXCLUDED.temp_max_c,
            temp_min_c = EXCLUDED.temp_min_c,
            precipitation_mm = EXCLUDED.precipitation_mm,
            wind_speed_max_kmh = EXCLUDED.wind_speed_max_kmh,
            raw_json = EXCLUDED.raw_json,
            pulled_at = now();
    """

    for i, day in enumerate(dates):
        day_record = {
            "time": day,
            "temperature_2m_max": daily["temperature_2m_max"][i],
            "temperature_2m_min": daily["temperature_2m_min"][i],
            "precipitation_sum": daily["precipitation_sum"][i],
            "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
        }
        cur.execute(upsert_sql, {
            "date": day,
            "lat": data["latitude"],
            "lon": data["longitude"],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precip": daily["precipitation_sum"][i],
            "wind_max": daily["wind_speed_10m_max"][i],
            "raw": psycopg2.extras.Json(day_record),
        })

    conn.commit()
    print(f"Upserted {len(dates)} days of weather.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    data = fetch_weather()
    upsert_weather(data)