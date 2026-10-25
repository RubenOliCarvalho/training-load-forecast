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


# Optional: press Enter to skip (e.g. on days the scale doesn't report it).
# Accepts a fraction (0.407) or a percentage (40.7); both are stored as 40.7.
def get_input_body_fat():
    while True:
        raw = input("Body fat (e.g. 0.407 or 40.7) [optional, Enter to skip]: ").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            print("Enter a number, e.g. 0.407 or 40.7, or leave blank")
            continue
        pct = round(value * 100, 1) if value < 1 else value
        if 1 <= pct <= 90:
            return pct
        print("That doesn't look like a realistic body fat percentage — try again.")


def get_input_muscle_mass():
    while True:
        raw = input("Muscle mass (kg) [optional, Enter to skip]: ").strip()
        if not raw:
            return None
        try:
            kg = float(raw)
        except ValueError:
            print("Enter a number, e.g. 59.3, or leave blank")
            continue
        if 10 <= kg <= 150:
            return kg
        print("That doesn't look like a realistic muscle mass in kg — try again.")


# Re-logging a date replaces that day's whole entry with the latest one.
def upsert_weight(conn, log_date, weight_kg, body_fat_pct, muscle_mass_kg):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staging.weight_log_raw (log_date, weight_kg, body_fat_pct, muscle_mass_kg, logged_at)
            values (%s, %s, %s, %s, now())
            on conflict (log_date) do update
                set weight_kg = excluded.weight_kg,
                    body_fat_pct = excluded.body_fat_pct,
                    muscle_mass_kg = excluded.muscle_mass_kg,
                    logged_at = excluded.logged_at
            """,
            (log_date, weight_kg, body_fat_pct, muscle_mass_kg),
        )
    conn.commit()


def main():
    log_date = get_input_date()
    weight_kg = get_input_weight()
    body_fat_pct = get_input_body_fat()
    muscle_mass_kg = get_input_muscle_mass()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        upsert_weight(conn, log_date, weight_kg, body_fat_pct, muscle_mass_kg)
        extras = []
        if body_fat_pct is not None:
            extras.append(f"body fat {body_fat_pct}%")
        if muscle_mass_kg is not None:
            extras.append(f"muscle mass {muscle_mass_kg} kg")
        print(f"Logged {weight_kg} kg{' · ' + ' · '.join(extras) if extras else ''} for {log_date.isoformat()}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()