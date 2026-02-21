-- tests/assert_btc_price_reasonable.sql
/*
Test: Bitcoin price should be in a reasonable range
Rationale: Detect obviously wrong prices
*/

SELECT
    symbol,
    price_usd,
    'Price too low (< $1,000)' AS issue
FROM {{ ref('stg_crypto_prices') }}
WHERE symbol = 'BTC'
  AND price_usd < 1000

UNION ALL

SELECT
    symbol,
    price_usd,
    'Price too high (> $500,000)' AS issue
FROM {{ ref('stg_crypto_prices') }}
WHERE symbol = 'BTC'
  AND price_usd > 500000
