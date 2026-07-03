with int_sales as (

    select * from {{ ref('int_sales') }}

),

dim_customer as (

    select customer_id from {{ ref('dim_customer') }}

),

dim_product as (

    select product_id from {{ ref('dim_product') }}

),

dim_store as (

    select store_id from {{ ref('dim_store') }}

),

fact as (

    select
        s.order_id,
        s.customer_id,
        s.product_id,
        s.store_id,
        s.order_date                                    as date_id,
        s.quantity,
        s.unit_price,
        s.line_revenue,
        s.payment_id,
        s.payment_amount,
        s.payment_status,
        s.is_paid

    from int_sales s
    where s.customer_id in (select customer_id from dim_customer)
      and s.product_id in (select product_id from dim_product)

)

select * from fact