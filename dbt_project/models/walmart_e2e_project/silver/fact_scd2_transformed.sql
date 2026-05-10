{{ 
    config
        (
            materialized='incremental',
            alias='fact_scd2',
            pre_hook="{{ copy_csv('fact_copy', '@WALMART_PROJECT_DB.BRONZE.WALMART_PROJECT_STAGE/fact.csv') }}",
            database='WALMART_PROJECT_DB',
            unique_key=['Store_id', 'Store_date', 'vrsn_start_date'],
            on_schema_change='append_new_columns',
            schema='SILVER'
        )
}}

with fact_scd2_renamed AS(

select
    cast(Store as Int) as Store_id,
    cast(Date as Timestamp) as Store_Date,
    cast(Temperature as Decimal) as Store_temperature,
    cast(Fuel_Price as Decimal) as Fuel_price,
    cast(MarkDown1 as Decimal) as Markdown1,
    cast(MarkDown2 as Decimal) as Markdown2,
    cast(MarkDown3 as Decimal) as Markdown3,
    cast(MarkDown4 as Decimal) as Markdown4,
    cast(MarkDown5 as Decimal) as Markdown5,
    cast(CPI as Decimal) as CPI,
    cast(unemployment as Decimal) as Unemployment,
    cast(isHoliday as varchar(10)) as Isholiday,
    current_timestamp as vrsn_start_date,
    null as vrsn_end_date,
    current_timestamp as Insert_date,
    current_timestamp as Update_date
from {{ref('fact_snapshot')}}
)

select *
from fact_scd2_renamed