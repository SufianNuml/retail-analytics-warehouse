with source as (

    select * from {{ source('raw', 'products') }}

),

renamed as (

    select
        product_id,
        trim(product_name)                          as product_name,
        lower(trim(category))                       as category,
        cast(price as decimal(10, 2))               as price,
        _loaded_at

    from source
    where price is not null
      and cast(price as decimal(10, 2)) > 0

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by product_id
        order by _loaded_at desc
    ) = 1

)

select * from deduplicated