with source as (

    select * from {{ source('raw', 'orders') }}

),

renamed as (

    select
        order_id,
        customer_id,
        product_id,
        store_id,
        cast(order_date as date)            as order_date,
        cast(quantity as integer)           as quantity,
        _loaded_at

    from source
    where order_id is not null
      and cast(order_date as date) <= current_date()

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by order_id
        order by _loaded_at desc
    ) = 1

)

select * from deduplicated