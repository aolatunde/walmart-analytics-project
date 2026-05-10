{{
    config
    (
        materialized='incremental',
        incremental_strategy='merge',
        pre_hook="{{ copy_csv('department_copy', '@WALMART_PROJECT_DB.BRONZE.WALMART_PROJECT_STAGE/department.csv') }}",
        unique_key=['Store_id', 'Dept_id', 'Store_Date'],
        merge_exclude_columns=['Insert_date'],
        on_schema_change='append_new_columns',
        schema='SILVER'
    )
}}


with department_renamed as
(
    select
        cast(Store as Int) as Store_id,
        cast(Dept as Int) as Dept_id,
        cast(Date as Timestamp) as Store_Date,
        cast(Weekly_Sales as Decimal) as Store_Weekly_sales,
        cast(IsHoliday as Varchar) as Isholiday,
        current_timestamp as Insert_date,
        current_timestamp as Update_date
    from {{source('bronze', 'department_copy')}}

    {% if is_incremental() %}
    where Insert_date > (select max(Insert_date) from {{this}} )
    {% endif%}


)
select * from department_renamed