with source as (

    select *
    from {{ source('raw', 'customers') }}

),

renamed as (

    select
        customer_id,
        name as customer_name,
        lower(trim(email)) as email,
        trim(country) as country,
        cast(created_at as timestamp) as created_at,
        _loaded_at

    from source

),

deduplicated as (

    select *
    from renamed

    qualify row_number() over(

        partition by customer_id
        order by _loaded_at desc

    ) = 1

)

select *
from deduplicated