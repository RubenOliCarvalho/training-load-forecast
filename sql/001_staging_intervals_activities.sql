CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.intervals_activities_raw (
    activity_id       text PRIMARY KEY,
    athlete_id        text,
    start_date_local  timestamp,
    start_date_utc    timestamptz,
    activity_type     text,
    source            text,
    training_load     numeric,
    ctl               numeric,
    atl               numeric,
    moving_time_secs  integer,
    elapsed_time_secs integer,
    avg_heartrate     numeric,
    max_heartrate     numeric,
    calories          numeric,
    raw_json          jsonb NOT NULL,
    pulled_at         timestamptz NOT NULL DEFAULT now()
);