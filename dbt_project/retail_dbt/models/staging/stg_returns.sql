with source as (

    select * from {{ source('raw', 'returns') }}

),

renamed as (

    select
        return_id,
        order_id,
        product_id,
        cast(return_date as date)               as return_date,
        trim(reason)                            as return_reason,
        cast(refund_amount as decimal(10, 2))   as refund_amount,
        lower(trim(status))                     as return_status,
        _loaded_at

    from source
    where return_id is not null
      and order_id is not null

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by return_id
        order by _loaded_at desc
    ) = 1

)

select * from deduplicated