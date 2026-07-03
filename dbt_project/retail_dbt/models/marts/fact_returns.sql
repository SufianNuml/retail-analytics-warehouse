with int_returns as (

    select * from {{ ref('int_returns') }}

),

fact as (

    select
        r.return_id,
        r.order_id,
        r.customer_id,
        r.product_id,
        r.return_date                                   as date_id,
        r.order_date,
        r.return_reason,
        r.refund_amount,
        r.return_status,
        r.original_order_revenue,
        r.refund_as_pct_of_revenue,
        r.days_to_return

    from int_returns r
    where r.return_id is not null

)

select * from fact