-- models/marts/dim_date.sql
/*
Date dimension table

Purpose: Calendar dimension for time-based analysis
Provides date attributes for filtering and grouping
*/

{{ config(
    materialized='table',
    unique_key='date_key'
) }}

WITH date_spine AS (
    -- Generate dates for the last year and next month
    SELECT
        CURRENT_DATE - INTERVAL '1 year' + (n || ' days')::INTERVAL AS date_day
    FROM generate_series(0, 365 + 30) AS n
)

SELECT
    TO_CHAR(date_day, 'YYYYMMDD')::INTEGER AS date_key,
    date_day AS date,
    EXTRACT(YEAR FROM date_day)::INTEGER AS year,
    EXTRACT(QUARTER FROM date_day)::INTEGER AS quarter,
    EXTRACT(MONTH FROM date_day)::INTEGER AS month,
    EXTRACT(WEEK FROM date_day)::INTEGER AS week_of_year,
    EXTRACT(DAY FROM date_day)::INTEGER AS day_of_month,
    EXTRACT(DOW FROM date_day)::INTEGER AS day_of_week,
    TO_CHAR(date_day, 'Day') AS day_name,
    TO_CHAR(date_day, 'Month') AS month_name,
    CASE 
        WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend,
    CASE 
        WHEN date_day = DATE_TRUNC('month', date_day) THEN TRUE 
        ELSE FALSE 
    END AS is_month_start,
    CASE 
        WHEN date_day = DATE_TRUNC('month', date_day) + INTERVAL '1 month' - INTERVAL '1 day' 
        THEN TRUE 
        ELSE FALSE 
    END AS is_month_end
FROM date_spine
