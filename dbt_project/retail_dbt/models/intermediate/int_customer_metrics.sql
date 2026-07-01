with sales as (

    select * from {{ ref('int_sales') }}

),

customer_orders as (

    select
        customer_id,
        count(distinct order_id)            as total_orders,
        sum(line_revenue)                   as total_revenue,
        min(order_date)                     as first_order_date,
        max(order_date)                     as last_order_date,
        count(distinct category)            as distinct_categories_purchased

    from sales
    where is_paid = true
    group by customer_id

),

customer_metrics as (

    select
        customer_id,
        total_orders,
        total_revenue,
        first_order_date,
        last_order_date,
        distinct_categories_purchased,
        total_revenue / nullif(total_orders, 0)     as avg_order_value,
        case
            when total_orders > 1   then true
            else false
        end                                         as is_repeat_customer,
        datediff('day', first_order_date, last_order_date) as customer_lifespan_days

    from customer_orders

)

select * from customer_metrics