-- macros/test_data_freshness.sql
{% test data_not_stale(model, column_name, max_age_hours=24) %}

WITH stale_data AS (
    SELECT
        {{ column_name }} AS updated_at,
        CURRENT_TIMESTAMP AS current_time,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - {{ column_name }})) / 3600 AS age_hours
    FROM {{ model }}
)

SELECT *
FROM stale_data
WHERE age_hours > {{ max_age_hours }}

{% endtest %}
