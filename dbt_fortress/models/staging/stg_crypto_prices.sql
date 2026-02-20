-- models/staging/stg_crypto_prices.sql
/*
Staging model for crypto prices

Purpose: Clean and standardize raw crypto price data
*/

{{ config(
    materialized='view'
) }}

SELECT
    id AS crypto_id,
    UPPER(symbol) AS symbol,
    name AS crypto_name,
    
    -- Price metrics
    current_price::NUMERIC AS price_usd,
    market_cap::NUMERIC AS market_cap_usd,
    total_volume::NUMERIC AS volume_24h_usd,
    price_change_24h::NUMERIC AS price_change_pct_24h,
    
    -- Metadata
    last_updated::TIMESTAMP AS price_updated_at,
    _airbyte_extracted_at::TIMESTAMP AS extracted_at,
    
    -- Derived
    CURRENT_TIMESTAMP AS dbt_loaded_at

FROM {{ source('raw', 'crypto_prices') }}

-- Filter out invalid records
WHERE current_price IS NOT NULL
  AND current_price > 0
  AND symbol IS NOT NULL
