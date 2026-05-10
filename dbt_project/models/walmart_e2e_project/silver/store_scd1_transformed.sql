{{
    config
    (
        materialized='incremental',
        incremental_strategy='merge',
        pre_hook="{{ copy_csv('store_copy', '@WALMART_PROJECT_DB.BRONZE.WALMART_PROJECT_STAGE/store.csv') }}",
        unique_key='Store_id',
        on_schema_change='append_new_columns',
        merge_exclude_columns=['Insert_date'],
        schema='SILVER'
    )
}}


with store_renamed as
(
    select
        cast(Store as Int) as Store_id,
        cast(Type as Varchar()) as Store_type,
        cast(Size as Varchar()) as Store_size,
        CURRENT_TIMESTAMP as Insert_date,
        CURRENT_TIMESTAMP as Update_date
    from {{source('bronze', 'store_copy')}}

    {% if is_incremental() %}
    where Insert_date > (select max(Insert_date) from {{this}} )
    {% endif%}


)
select * from store_renamed