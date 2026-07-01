with orders as (

    select * from {{ ref('stg_orders') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

payments as (

    select * from {{ ref('stg_payments') }}

),

sales_enriched as (

    select
        o.order_id,
        o.customer_id,
        o.product_id,
        o.store_id,
        o.order_date,
        o.quantity,
        p.product_name,
        p.category,
        p.price                                         as unit_price,
        o.quantity * p.price                            as line_revenue,
        pay.payment_id,
        pay.payment_amount,
        pay.payment_status,
        case
            when pay.payment_status = 'completed'   then true
            when pay.payment_status = 'paid'        then true
            else false
        end                                             as is_paid

    from orders o
    left join products p
        on o.product_id = p.product_id
    left join payments pay
        on o.order_id = pay.order_id

)

select * from sales_enriched