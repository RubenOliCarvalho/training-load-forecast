CREATE TABLE staging.weather_daily (
    weather_date        date PRIMARY KEY,
    latitude             numeric,
    longitude            numeric,
    temp_max_c           numeric,
    temp_min_c           numeric,
    precipitation_mm     numeric,
    wind_speed_max_kmh   numeric,
    raw_json             jsonb NOT NULL,
    pulled_at            timestamptz NOT NULL DEFAULT now()
);