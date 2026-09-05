with training as (

    select * from {{ ref('int_training_load_daily') }}

),

fixed_weather as (

    select * from {{ ref('stg_weather_daily') }}

),

daily_activity_agg as (

    select
        start_date_local::date as activity_date,
        count(*) as activity_count,
        sum(calories) as total_calories,
        sum(distance_km) as total_distance_km,
        sum(moving_time_min) as total_moving_time_min,
        sum(avg_heartrate * moving_time_min)
         / nullif(sum(moving_time_min) filter (where avg_heartrate is not null), 0)
        as avg_heartrate_weighted
    from {{ ref('stg_intervals_activities') }}
    group by 1

),

garmin_outdoor_temp as (

    select
        start_date_local::date as activity_date,
        avg(avg_temp_c) as garmin_avg_temp_c,
        min(min_temp_c) as garmin_min_temp_c,
        max(max_temp_c) as garmin_max_temp_c,
        count(*) as outdoor_activity_count
    from {{ ref('stg_intervals_activities') }}
    where activity_type in ('Ride', 'Run', 'TrailRun')
    group by 1

),

exercise_calorie_target as (

    select target_min, target_max
    from {{ ref('targets') }}
    where metric = 'exercise_calories' and period = 'day'

)

select
    t.calendar_date,
    t.daily_training_load,
    t.ctl,
    t.atl,
    t.tsb,
    coalesce(a.activity_count, 0) as activity_count,
    (coalesce(a.activity_count, 0) > 0) as is_active_day,
    coalesce(a.total_calories, 0) as total_calories,
    case
        when coalesce(a.activity_count, 0) = 0 then 0
        else a.total_distance_km
    end as total_distance_km,
    coalesce(a.total_moving_time_min, 0) as total_moving_time_min,
    a.avg_heartrate_weighted,
    fw.temp_max_c as location_temp_max_c,
    fw.temp_min_c as location_temp_min_c,
    fw.precipitation_mm,
    fw.wind_speed_max_kmh,
    g.garmin_avg_temp_c,
    g.garmin_min_temp_c,
    g.garmin_max_temp_c,
    g.outdoor_activity_count,
    ect.target_min as exercise_calorie_target_min,
    ect.target_max as exercise_calorie_target_max,
    case
        when coalesce(a.total_calories, 0) < ect.target_min then 'below_target'
        when coalesce(a.total_calories, 0) > ect.target_max then 'above_target'
        else 'within_target'
    end as exercise_calorie_target_status
from training t
left join daily_activity_agg a
    on a.activity_date = t.calendar_date
left join fixed_weather fw
    on fw.weather_date = t.calendar_date
left join garmin_outdoor_temp g
    on g.activity_date = t.calendar_date
cross join exercise_calorie_target ect
order by t.calendar_date