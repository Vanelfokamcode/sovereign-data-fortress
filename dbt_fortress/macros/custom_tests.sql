{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
    Generate schema name for models
    
    Purpose: Organize models into schemas based on layer
    (staging, intermediate, marts)
    
    Usage: Automatically applied by dbt based on dbt_project.yml config
    #}
    
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}

{% macro cents_to_dollars(column_name, scale=2) %}
    {#
    Convert cents to dollars
    
    Args:
        column_name (str): Column containing cent values
        scale (int): Decimal places (default: 2)
    
    Returns:
        Numeric value in dollars
    
    Example:
        {{ cents_to_dollars('amount_cents') }}
        -- Converts 12345 cents → 123.45 dollars
    #}
    
    ({{ column_name }} / 100.0)::NUMERIC(16, {{ scale }})
{% endmacro %}
