with source as (

    select * from {{ source('raw', 'payments') }}

),

renamed as (

    select
        payment_id,
        order_id,
        cast(amount as decimal(10, 2))      as payment_amount,
        lower(trim(status))                 as payment_status,
        _loaded_at

    from source
    where payment_id is not null
      and order_id is not null

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by payment_id
        order by _loaded_at desc
    ) = 1

)

select * from deduplicated