with customers as (

    select * from {{ ref('stg_customers') }}

),

customer_metrics as (

    select * from {{ ref('int_customer_metrics') }}

),

final as (

    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.country,
        c.created_at                                        as customer_since,
        coalesce(m.total_orders, 0)                         as total_orders,
        coalesce(m.total_revenue, 0)                        as total_revenue,
        coalesce(m.avg_order_value, 0)                      as avg_order_value,
        m.first_order_date,
        m.last_order_date,
        coalesce(m.is_repeat_customer, false)               as is_repeat_customer,
        coalesce(m.customer_lifespan_days, 0)               as customer_lifespan_days,
        coalesce(m.distinct_categories_purchased, 0)        as distinct_categories_purchased

    from customers c
    left join customer_metrics m
        on c.customer_id = m.customer_id

)

select * from final