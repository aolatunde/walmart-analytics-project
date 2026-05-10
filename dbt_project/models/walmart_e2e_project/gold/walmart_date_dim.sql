{{
    config
    (
        materialized='table',
        schema='GOLD'
    )
}}

with walmart_date_dim as (
    select distinct
        to_number(to_char(Store_Date, 'YYYYMMDD')) as Date_id,
        Store_Date,
        Isholiday,
        Insert_date,
        Update_date
    from {{ ref("department_scd1_transformed")}}
)

select * from walmart_date_dim
