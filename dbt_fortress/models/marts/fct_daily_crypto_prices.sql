-- models/marts/fct_daily_crypto_prices.sql
/*
Fact table: Daily cryptocurrency prices

Purpose: Daily grain fact table with OHLC prices and metrics
Star schema center - joins to dim_crypto and dim_date

Grain: One row per cryptocurrency per day
*/

{{ config(
    materialized='table',
    unique_key=['crypto_key', 'date_key']
) }}

WITH daily_agg AS (
    SELECT * FROM {{ ref('int_crypto_daily_aggregates') }}
),

crypto_dim AS (
    SELECT * FROM {{ ref('dim_crypto') }}
),

date_dim AS (
    SELECT * FROM {{ ref('dim_date') }}
)

SELECT
    -- Surrogate keys
    crypto_dim.crypto_key,
    date_dim.date_key,
    
    -- Natural keys (for readability)
    daily_agg.crypto_id,
    daily_agg.symbol,
    daily_agg.price_date,
    
    -- OHLC (Open, High, Low, Close)
    daily_agg.price_open,
    daily_agg.price_high,
    daily_agg.price_low,
    daily_agg.price_close,
    
    -- Additional metrics
    daily_agg.price_avg,
    daily_agg.avg_volume_24h AS volume_24h,
    daily_agg.avg_market_cap AS market_cap,
    daily_agg.volatility_pct,
    
    -- Price changes
    daily_agg.price_close - daily_agg.price_open AS price_change,
    CASE 
        WHEN daily_agg.price_open > 0 
        THEN ((daily_agg.price_close - daily_agg.price_open) / daily_agg.price_open * 100)
        ELSE NULL
    END AS price_change_pct,
    
    -- Data quality
    daily_agg.data_points_count,
    daily_agg.first_update_at,
    daily_agg.last_update_at,
    
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_loaded_at

FROM daily_agg
INNER JOIN crypto_dim ON daily_agg.crypto_id = crypto_dim.crypto_id
INNER JOIN date_dim ON daily_agg.price_date = date_dim.date
