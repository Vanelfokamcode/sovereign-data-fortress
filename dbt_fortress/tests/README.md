# dbt Tests Documentation

## Test Strategy

Our data quality strategy uses 4 layers of testing:

### 1. Schema Tests (Built-in)
- `unique`: Ensures no duplicate records
- `not_null`: Ensures required fields are present
- `accepted_values`: Validates enum-like fields
- `relationships`: Validates foreign key integrity

### 2. Data Tests (Custom SQL)
Located in `tests/` directory:
- `assert_no_future_prices.sql`: Detects time-travel data
- `assert_btc_exists.sql`: Ensures Bitcoin is always present
- `assert_btc_price_reasonable.sql`: Range validation for BTC price

### 3. Generic Tests (Reusable Macros)
Located in `macros/`:
- `test_data_freshness.sql`: Detects stale data
- `test_reasonable_percent_change.sql`: Validates percentage changes

### 4. dbt-utils Tests (Package)
Advanced tests from dbt_utils:
- `expression_is_true`: Custom SQL expressions
- `recency`: Data freshness checks

## Running Tests
```bash
# All tests
dbt test

# Specific model
dbt test --select stg_crypto_prices

# Specific test type
dbt test --select test_type:schema
dbt test --select test_type:data

# Fail on first error
dbt test --fail-fast
```

## Test Severity

- `error`: Test failure stops the pipeline
- `warn`: Test failure logs warning but continues

## Adding New Tests

1. Schema tests: Add to `models/staging/schema.yml`
2. Data tests: Create SQL file in `tests/`
3. Generic tests: Create macro in `macros/`
