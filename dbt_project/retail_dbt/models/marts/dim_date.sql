with date_spine as (

    select
        dateadd('day', seq4(), '2020-01-01'::date) as date_day
    from table(generator(rowcount => 2922))  -- ~8 years of dates (2020–2027)

),

final as (

    select
        date_day                                        as date_id,
        date_day,
        year(date_day)                                  as year,
        month(date_day)                                 as month_number,
        monthname(date_day)                             as month_name,
        quarter(date_day)                               as quarter_number,
        concat('Q', quarter(date_day))                  as quarter_label,
        weekofyear(date_day)                            as week_of_year,
        dayofweek(date_day)                             as day_of_week_number,
        dayname(date_day)                               as day_of_week_name,
        case
            when dayofweek(date_day) in (0, 6) then true
            else false
        end                                             as is_weekend,
        concat(year(date_day), '-',
               lpad(month(date_day), 2, '0'))           as year_month

    from date_spine

)

select * from final