{% macro scd2_merge(target_table, stream_table, key_columns, tracked_columns) %}

-- Step 1: Expire old records when data changes
MERGE INTO {{ target_table }} T
USING {{ stream_table }} S
ON
{% for col in key_columns %}
T.{{ col }} = S.{{ col }}
{% if not loop.last %} AND {% endif %}
{% endfor %}
AND T.IS_CURRENT = TRUE

WHEN MATCHED AND (
{% for col in tracked_columns %}
T.{{ col }} <> S.{{ col }}
{% if not loop.last %} OR {% endif %}
{% endfor %}
)
THEN UPDATE SET
T.VALID_TO = CURRENT_TIMESTAMP,
T.IS_CURRENT = FALSE;

-- Step 2: Insert new version
INSERT INTO {{ target_table }}
(
{% for col in key_columns %}
{{ col }},
{% endfor %}
{% for col in tracked_columns %}
{{ col }},
{% endfor %}
VALID_FROM,
VALID_TO,
IS_CURRENT
)

SELECT
{% for col in key_columns %}
S.{{ col }},
{% endfor %}
{% for col in tracked_columns %}
S.{{ col }},
{% endfor %}
CURRENT_TIMESTAMP,
NULL,
TRUE
FROM {{ stream_table }} S;

{% endmacro %}