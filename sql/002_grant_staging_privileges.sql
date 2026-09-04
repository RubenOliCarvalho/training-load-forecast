GRANT USAGE ON SCHEMA staging TO training_load;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA staging TO training_load;

-- Ensures any table created in `staging` from now on (like the weather
-- table we're about to build) automatically grants training_load the
-- same rights, without needing this fixed again per-table.
ALTER DEFAULT PRIVILEGES IN SCHEMA staging
    GRANT SELECT, INSERT, UPDATE ON TABLES TO training_load;