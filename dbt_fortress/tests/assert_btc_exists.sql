-- tests/assert_btc_exists.sql
/*
Test: Ensure Bitcoin (BTC) is always in the dataset
Rationale: BTC is the #1 crypto, must always be present
*/

WITH btc_count AS (
    SELECT COUNT(*) AS count
    FROM {{ ref('stg_crypto_prices') }}
    WHERE symbol = 'BTC'
)
SELECT *
FROM btc_count
WHERE count = 0
