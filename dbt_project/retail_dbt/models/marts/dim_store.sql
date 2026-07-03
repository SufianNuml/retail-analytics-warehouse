with stores as (

    select * from {{ ref('stg_stores') }}

),

final as (

    select
        store_id,
        city,
        store_country

    from stores

)

select * from final