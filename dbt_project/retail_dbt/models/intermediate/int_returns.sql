with returns as (

    select * from {{ ref('stg_returns') }}

),

sales as (

    select
        order_id,
        order_date,
        customer_id,
        product_id,
        product_name,
        category,
        line_revenue

    from {{ ref('int_sales') }}

),

returns_enriched as (

    select
        r.return_id,
        r.order_id,
        r.return_date,
        r.return_reason,
        r.refund_amount,
        r.return_status,
        s.order_date,
        s.customer_id,
        s.product_id,
        s.product_name,
        s.category,
        s.line_revenue                                      as original_order_revenue,
        r.refund_amount / nullif(s.line_revenue, 0)         as refund_as_pct_of_revenue,
        datediff('day', s.order_date, r.return_date)        as days_to_return

    from returns r
    left join sales s
        on r.order_id = s.order_id

)

select * from returns_enriched