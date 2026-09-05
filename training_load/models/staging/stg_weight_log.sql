select
    log_date,
    weight_kg,
    logged_at
from {{ source('staging', 'weight_log_raw') }}