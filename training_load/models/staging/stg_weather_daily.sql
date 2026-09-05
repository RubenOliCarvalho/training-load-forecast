select
    weather_date,
    latitude,
    longitude,
    temp_max_c,
    temp_min_c,
    precipitation_mm,
    wind_speed_max_kmh,
    pulled_at
from {{ source('staging', 'weather_daily') }}