create table if not exists staging.weight_log_raw (
    log_date date primary key,
    weight_kg numeric(5,2) not null,
    logged_at timestamp not null default now()
);