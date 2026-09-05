with daily as (

    select * from {{ ref('mart_daily_training') }}

),

weekly_agg as (

    select
        date_trunc('week', calendar_date)::date as week_start,
        count(*) as days_in_week,
        count(*) filter (where is_active_day) as active_days,
        round(
            count(*) filter (where is_active_day)::numeric / count(*), 3
        ) as active_day_rate,
        sum(total_distance_km) as total_distance_km,
        count(*) filter (where is_active_day and total_distance_km is null) as active_days_missing_distance,
        sum(total_calories) as total_calories,
        round(sum(total_moving_time_min) / 60.0, 1) as total_moving_time_hours,
        sum(total_moving_time_min * avg_heartrate_weighted)
            / nullif(sum(total_moving_time_min) filter (where avg_heartrate_weighted is not null), 0)
            as avg_heartrate_weighted,
        round(avg(ctl), 2) as avg_ctl,
        round(avg(atl), 2) as avg_atl,
        round(avg(tsb), 2) as avg_tsb,
        round(avg(weight_kg), 1) as avg_weight_kg,
        round(avg(location_temp_max_c), 1) as avg_location_temp_max_c,
        round(avg(location_temp_min_c), 1) as avg_location_temp_min_c,
        round(sum(precipitation_mm), 1) as total_precipitation_mm
    from daily
    group by 1

),

exercise_calorie_target as (

    select target_min, target_max
    from {{ ref('targets') }}
    where metric = 'exercise_calories' and period = 'week'

),

exercise_minutes_target as (

    select target_min, target_max
    from {{ ref('targets') }}
    where metric = 'exercise_minutes' and period = 'week'

)

select
    w.*,
    ect.target_min as exercise_calorie_target_min,
    ect.target_max as exercise_calorie_target_max,
    case
        when w.total_calories < ect.target_min then 'below_target'
        when w.total_calories > ect.target_max then 'above_target'
        else 'within_target'
    end as exercise_calorie_target_status,
    emt.target_min as exercise_minutes_target_min,
    emt.target_max as exercise_minutes_target_max,
    case
        when w.total_moving_time_hours * 60 < emt.target_min then 'below_target'
        when w.total_moving_time_hours * 60 > emt.target_max then 'above_target'
        else 'within_target'
    end as exercise_minutes_target_status
from weekly_agg w
cross join exercise_calorie_target ect
cross join exercise_minutes_target emt
order by w.week_start