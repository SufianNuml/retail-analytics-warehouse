with source as (

    select * from {{ source('raw', 'stores') }}

),

renamed as (

    select
        store_id,
        trim(city)                      as city,
        trim(country)                   as store_country,
        _loaded_at

    from source
    where store_id is not null

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by store_id
        order by _loaded_at desc
    ) = 1

)

select * from deduplicated