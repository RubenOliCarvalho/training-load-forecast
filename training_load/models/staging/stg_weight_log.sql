select
    log_date,
    weight_kg,
    body_fat_pct,
    muscle_mass_pct,
    logged_at
from {{ source('staging', 'weight_log_raw') }}
