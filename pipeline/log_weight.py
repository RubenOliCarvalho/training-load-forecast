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
def get_input_pct(label):
    while True:
        raw = input(f"{label} (%) [optional, Enter to skip]: ").strip()
        if not raw:
            return None
        try:
            pct = float(raw)
        except ValueError:
            print("Enter a number, e.g. 24.5, or leave blank")
            continue
        if 1 <= pct <= 90:
            return pct
        print("That doesn't look like a realistic percentage — try again.")


# Re-logging a date replaces that day's whole entry with the latest one.
def upsert_weight(conn, log_date, weight_kg, body_fat_pct, muscle_mass_pct):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staging.weight_log_raw (log_date, weight_kg, body_fat_pct, muscle_mass_pct, logged_at)
            values (%s, %s, %s, %s, now())
            on conflict (log_date) do update
                set weight_kg = excluded.weight_kg,
                    body_fat_pct = excluded.body_fat_pct,
                    muscle_mass_pct = excluded.muscle_mass_pct,
                    logged_at = excluded.logged_at
            """,
            (log_date, weight_kg, body_fat_pct, muscle_mass_pct),
        )
    conn.commit()


def main():
    log_date = get_input_date()
    weight_kg = get_input_weight()
    body_fat_pct = get_input_pct("Body fat")
    muscle_mass_pct = get_input_pct("Muscle mass")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        upsert_weight(conn, log_date, weight_kg, body_fat_pct, muscle_mass_pct)
        extras = [f"{label} {v}%" for label, v in (("body fat", body_fat_pct), ("muscle mass", muscle_mass_pct)) if v is not None]
        print(f"Logged {weight_kg} kg{' · ' + ' · '.join(extras) if extras else ''} for {log_date.isoformat()}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()