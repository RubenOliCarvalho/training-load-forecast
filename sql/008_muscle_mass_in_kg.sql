-- Muscle mass is reported by the scale in kg, not %. Existing values were
-- already entered as kg, so this only renames the column and widens it to
-- match weight_kg.
alter table staging.weight_log_raw rename column muscle_mass_pct to muscle_mass_kg;
alter table staging.weight_log_raw alter column muscle_mass_kg type numeric(5,2);
