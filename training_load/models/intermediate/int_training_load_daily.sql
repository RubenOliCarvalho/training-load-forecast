with recursive daily_load as (

    select
        start_date_local::date as activity_date,
        sum(training_load) as daily_training_load
    from {{ ref('stg_intervals_activities') }}
    group by 1

),

seed as (

    select
        start_date_local::date as seed_date,
        ctl_intervals as seed_ctl,
        atl_intervals as seed_atl
    from {{ ref('stg_intervals_activities') }}
    where start_date_local::date = (
        select min(start_date_local::date) from {{ ref('stg_intervals_activities') }}
    )
    order by start_date_local desc
    limit 1

),

calendar as (

    select generate_series(
        (select seed_date from seed),
        current_date,
        interval '1 day'
    )::date as calendar_date

),

daily_load_spine as (

    select
        c.calendar_date,
        coalesce(d.daily_training_load, 0) as daily_training_load
    from calendar c
    left join daily_load d
        on d.activity_date = c.calendar_date

),

recursive_ctl_atl as (

    -- anchor: seed date takes intervals.icu's own ctl/atl directly, not recomputed
    select
        seed_date as calendar_date,
        seed_ctl as ctl,
        seed_atl as atl
    from seed

    union all

    -- recursive step: each day builds on the prior day's computed ctl/atl
    select
        s.calendar_date,
        r.ctl + (s.daily_training_load - r.ctl) / 42.0 as ctl,
        r.atl + (s.daily_training_load - r.atl) / 7.0 as atl
    from recursive_ctl_atl r
    join daily_load_spine s
        on s.calendar_date = r.calendar_date + 1

)

select
    r.calendar_date,
    s.daily_training_load,
    r.ctl,
    r.atl,
    lag(r.ctl) over (order by r.calendar_date) - lag(r.atl) over (order by r.calendar_date) as tsb
from recursive_ctl_atl r
left join daily_load_spine s using (calendar_date)
order by r.calendar_date