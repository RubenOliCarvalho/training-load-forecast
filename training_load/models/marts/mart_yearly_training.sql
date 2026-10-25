with daily as (

    select * from {{ ref('mart_daily_training') }}

),

activities as (

    select * from {{ ref('stg_intervals_activities') }}

),

yearly_activity_agg as (

    select
        date_trunc('year', start_date_local)::date as year_start,
        count(*) as total_activities,
        count(distinct activity_type) as distinct_activity_types,
        round(sum(elevation_gain_m)::numeric, 0) as total_elevation_gain_m,
        round(max(moving_time_min)::numeric / 60.0, 2) as longest_activity_hours,
        round(max(distance_km)::numeric, 1) as longest_distance_km,
        round(sum(training_load)::numeric, 0) as total_training_load
    from activities
    group by 1

),

yearly_daily_agg as (

    select
        date_trunc('year', calendar_date)::date as year_start,
        -- days_tracked < 365 for the first year (history starts mid-year) and
        -- for the current year (still in progress)
        count(*) as days_tracked,
        min(calendar_date) as first_tracked_date,
        max(calendar_date) as last_tracked_date,
        count(*) filter (where is_active_day) as active_days,
        round(
            count(*) filter (where is_active_day)::numeric / count(*), 3
        ) as active_day_rate,
        round(sum(total_distance_km)::numeric, 1) as total_distance_km,
        sum(total_calories) as total_calories,
        round(sum(total_moving_time_min)::numeric / 60.0, 1) as total_moving_time_hours,
        round(avg(ctl)::numeric, 1) as avg_ctl,
        round(max(ctl)::numeric, 1) as peak_ctl,
        (array_agg(weight_kg order by calendar_date) filter (where weight_kg is not null))[1] as start_weight_kg,
        (array_agg(weight_kg order by calendar_date desc) filter (where weight_kg is not null))[1] as end_weight_kg,
        (array_agg(body_fat_pct order by calendar_date) filter (where body_fat_pct is not null))[1] as start_body_fat_pct,
        (array_agg(body_fat_pct order by calendar_date desc) filter (where body_fat_pct is not null))[1] as end_body_fat_pct,
        (array_agg(muscle_mass_kg order by calendar_date) filter (where muscle_mass_kg is not null))[1] as start_muscle_mass_kg,
        (array_agg(muscle_mass_kg order by calendar_date desc) filter (where muscle_mass_kg is not null))[1] as end_muscle_mass_kg
    from daily
    group by 1

)

select
    extract(year from d.year_start)::int as year,
    d.*,
    coalesce(a.total_activities, 0) as total_activities,
    a.distinct_activity_types,
    a.total_elevation_gain_m,
    a.longest_activity_hours,
    a.longest_distance_km,
    a.total_training_load
from yearly_daily_agg d
left join yearly_activity_agg a using (year_start)
order by d.year_start
