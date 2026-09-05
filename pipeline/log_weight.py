import os
from datetime import date

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_input_date():
    today = date.today()
    raw = input(f"Date [default: today, {today.isoformat()}]: ").strip()
    if not raw:
        return today
    return date.fromisoformat(raw)


def get_input_weight():
    while True:
        raw = input("Weight (kg): ").strip()
        try:
            weight = float(raw)
        except ValueError:
            print("Enter a number, e.g. 108.4")
            continue
        if 30 <= weight <= 300:
            return weight
        print("That doesn't look like a realistic weight in kg — try again.")


def upsert_weight(conn, log_date, weight_kg):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staging.weight_log_raw (log_date, weight_kg, logged_at)
            values (%s, %s, now())
            on conflict (log_date) do update
                set weight_kg = excluded.weight_kg,
                    logged_at = excluded.logged_at
            """,
            (log_date, weight_kg),
        )
    conn.commit()


def main():
    log_date = get_input_date()
    weight_kg = get_input_weight()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        upsert_weight(conn, log_date, weight_kg)
        print(f"Logged {weight_kg} kg for {log_date.isoformat()}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()