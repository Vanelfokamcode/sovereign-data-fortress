-- models/intermediate/int_crypto_daily_aggregates.sql
/*
Intermediate model: Daily crypto price aggregates

Purpose: Aggregate hourly staging data into daily summaries
*/

{{ config(
    materialized='view'
) }}

WITH ordered_prices AS (
    SELECT
        crypto_id,
        symbol,
        crypto_name,
        DATE(price_updated_at) AS price_date,
        price_usd,
        price_updated_at,
        volume_24h_usd,
        market_cap_usd,
        ROW_NUMBER() OVER (
            PARTITION BY crypto_id, DATE(price_updated_at)
            ORDER BY price_updated_at ASC
        ) AS rn_first,
        ROW_NUMBER() OVER (
            PARTITION BY crypto_id, DATE(price_updated_at)
            ORDER BY price_updated_at DESC
        ) AS rn_last
    FROM {{ ref('stg_crypto_prices') }}
),

first_prices AS (
    SELECT
        crypto_id,
        price_date,
        price_usd AS price_open
    FROM ordered_prices
    WHERE rn_first = 1
),

last_prices AS (
    SELECT
        crypto_id,
        price_date,
        price_usd AS price_close
    FROM ordered_prices
    WHERE rn_last = 1
),

daily_stats AS (
    SELECT
        crypto_id,
        symbol,
        crypto_name,
        price_date,
        
        -- Price metrics
        MIN(price_usd) AS price_low,
        MAX(price_usd) AS price_high,
        AVG(price_usd) AS price_avg,
        
        -- Volume and market cap
        AVG(volume_24h_usd) AS avg_volume_24h,
        AVG(market_cap_usd) AS avg_market_cap,
        
        -- Data quality
        COUNT(*) AS data_points_count,
        MIN(price_updated_at) AS first_update_at,
        MAX(price_updated_at) AS last_update_at
        
    FROM ordered_prices
    GROUP BY crypto_id, symbol, crypto_name, price_date
)

SELECT
    s.crypto_id,
    s.symbol,
    s.crypto_name,
    s.price_date,
    
    -- OHLC
    f.price_open,
    l.price_close,
    s.price_low,
    s.price_high,
    s.price_avg,
    
    -- Metrics
    s.avg_volume_24h,
    s.avg_market_cap,
    
    -- Volatility (price range as percentage of average)
    CASE 
        WHEN s.price_avg > 0 
        THEN ROUND(((s.price_high - s.price_low) / s.price_avg * 100)::NUMERIC, 2)
        ELSE NULL
    END AS volatility_pct,
    
    -- Data quality
    s.data_points_count,
    s.first_update_at,
    s.last_update_at

FROM daily_stats s
LEFT JOIN first_prices f ON s.crypto_id = f.crypto_id AND s.price_date = f.price_date
LEFT JOIN last_prices l ON s.crypto_id = l.crypto_id AND s.price_date = l.price_date
