{{
    config
    (
        materialized ='table',
        schema='GOLD'
    )
}}

with walmart_store_dim as (

    select
        ss.Store_id,
        ss.Store_type,
        ss.Store_size,
        ss.Insert_date,
        ss.Update_date
    from {{ ref("store_scd1_transformed")}} ss
)

select * from walmart_store_dim
