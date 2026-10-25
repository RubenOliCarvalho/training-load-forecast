alter table staging.weight_log_raw
    add column if not exists body_fat_pct numeric(4,1),
    add column if not exists muscle_mass_pct numeric(4,1);
