-- tests/assert_no_future_prices.sql
/*
Test: Ensure no price updates are dated in the future
Rationale: Future-dated prices indicate data quality issues
*/

SELECT
    crypto_id,
    symbol,
    price_updated_at,
    CURRENT_TIMESTAMP AS current_time
FROM {{ ref('stg_crypto_prices') }}
WHERE price_updated_at > CURRENT_TIMESTAMP
