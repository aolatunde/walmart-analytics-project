{% snapshot fact_snapshot %}
    {{
        config(
            target_database='WALMART_PROJECT_DB',
            target_schema='snapshots',
            strategy='check',
            unique_key=['Store', 'Date'],
            check_cols=['Temperature', 'Fuel_Price', 'MarkDown1', 'MarkDown1', 'MarkDown1', 'MarkDown1', 'MarkDown1', 'CPI', 'unemployment', 'isHoliday']
        )
    }}

    select * from {{ source('bronze', 'fact_copy') }}
 {% endsnapshot %}