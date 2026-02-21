-- macros/test_reasonable_percent_change.sql
{% test reasonable_percent_change(model, column_name, min_value=-100, max_value=10000) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND ({{ column_name }} < {{ min_value }} OR {{ column_name }} > {{ max_value }})

{% endtest %}
