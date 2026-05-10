{{
    config
    (
        materialized ='table',
        schema='GOLD'
    )
}}

with walmart_fact_table as (

    select
        fs.Store_id,
        ds.Dept_id,
        fs.Store_Date,
        ds.Store_Weekly_sales,
        fs.Fuel_price,
        fs.Store_temperature,
        fs.Unemployment,
        fs.CPI,
        fs.Markdown1,
        fs.Markdown2,
        fs.Markdown3,
        fs.Markdown4,
        fs.Markdown5,
        fs.Insert_date,
        fs.Update_date,
        fs.Vrsn_start_date,
        fs.Vrsn_end_date
    from {{ ref("fact_scd2_transformed")}} fs
    join {{ ref("department_scd1_transformed")}} ds
    ON fs.Store_id = ds.Store_id AND fs.Store_Date = ds.Store_date
)

select * from walmart_fact_table
