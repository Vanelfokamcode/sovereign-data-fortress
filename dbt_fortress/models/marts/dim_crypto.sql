-- models/marts/dim_crypto.sql
/*
Cryptocurrency dimension table

Purpose: Master list of cryptocurrencies with attributes
Slowly Changing Dimension (Type 1 - overwrite)
*/

{{ config(
    materialized='table',
    unique_key='crypto_key'
) }}

WITH latest_crypto_data AS (
    SELECT DISTINCT
        crypto_id,
        symbol,
        crypto_name,
        ROW_NUMBER() OVER (PARTITION BY crypto_id ORDER BY dbt_loaded_at DESC) AS rn
    FROM {{ ref('stg_crypto_prices') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['crypto_id']) }} AS crypto_key,
    crypto_id,
    symbol,
    crypto_name,
    
    -- Categorization (simplified for demo)
    CASE
        WHEN symbol IN ('BTC') THEN 'Layer 1 - Proof of Work'
        WHEN symbol IN ('ETH') THEN 'Layer 1 - Proof of Stake'
        WHEN symbol IN ('SOL', 'ADA', 'DOT') THEN 'Layer 1 - Alternative'
        ELSE 'Other'
    END AS category,
    
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at
    
FROM latest_crypto_data
WHERE rn = 1
