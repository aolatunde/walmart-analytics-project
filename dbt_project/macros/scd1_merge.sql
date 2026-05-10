{% macro scd1_merge(target_table, stream_table, key_columns, column_list) %}

MERGE INTO {{ target_table }} T
USING {{ stream_table }} S
ON
{% for col in key_columns %}
    T.{{ col }} = S.{{ col }}{% if not loop.last %} AND {% endif %}
{% endfor %}

WHEN MATCHED THEN
UPDATE SET
{% for col in column_list if col not in key_columns %}
    T.{{ col }} = S.{{ col }}{% if not loop.last %},{% endif %}
{% endfor %}

WHEN NOT MATCHED THEN
INSERT
(
    {{ column_list | join(', ') }}
)
VALUES
(
{% for col in column_list %}
    S.{{ col }}{% if not loop.last %},{% endif %}
{% endfor %}
);

{% endmacro %}