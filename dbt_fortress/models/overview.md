{% docs __overview__ %}

# 🏰 Sovereign Data Fortress

## Project Overview

Welcome to the Sovereign Data Fortress dbt documentation!

This project demonstrates modern data engineering principles:
- Cloud-agnostic architecture
- Infrastructure as Code (Terraform)
- ELT pipeline (Extract-Load-Transform)
- Data contracts and quality testing
- Circuit breakers for resilience
- Living documentation (this site!)

---

## Architecture
```
┌─────────────────────────────────────────────┐
│  CoinGecko API                              │
│  (Cryptocurrency prices)                    │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  Ingestion Pipeline                         │
│  - Extract data                             │
│  - Validate with data contracts             │
│  - Circuit breaker protection               │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  MinIO (S3-compatible storage)              │
│  Raw data in Parquet format                 │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  PostgreSQL (raw schema)                    │
│  Staging area for dbt                       │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  dbt (this project!)                        │
│  - Staging: Clean & standardize             │
│  - Marts: Business metrics                  │
│  - Tests: Data quality                      │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  PostgreSQL (analytics schema)              │
│  Production-ready tables                    │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  Grafana / BI Tools                         │
│  Dashboards & analytics                     │
└─────────────────────────────────────────────┘
```

---

## Data Layers

### 🥉 Bronze: Raw Data
- **Location**: `raw` schema
- **Source**: MinIO (Parquet files)
- **Characteristics**: Untransformed, exactly as received
- **Refresh**: Hourly

### 🥈 Silver: Staging
- **Location**: `analytics.staging` schema
- **Purpose**: Clean, standardized, typed
- **Models**: `stg_*`
- **Characteristics**: 1:1 with source tables

### 🥇 Gold: Marts
- **Location**: `analytics.marts` schema
- **Purpose**: Business-ready metrics
- **Models**: `fct_*` (facts), `dim_*` (dimensions)
- **Characteristics**: Aggregated, denormalized

---

## Data Quality

### Protection Layers

1. **Data Contracts** (Pre-ingestion)
   - Pydantic schemas
   - Type validation
   - Business rules

2. **dbt Tests** (Post-transformation)
   - Schema tests (not_null, unique)
   - Data tests (custom SQL)
   - Generic tests (reusable macros)

3. **Circuit Breakers**
   - Automatic failure detection
   - Pipeline protection
   - Auto-recovery

---

## Quick Links

- **Models**: Browse all models in the sidebar
- **Sources**: See raw data sources
- **Tests**: View all data quality tests
- **Macros**: Reusable SQL functions
- **Lineage**: Click any model → "Lineage" tab

---

## Team

- **Owner**: Vanel fokam
- **GitHub**: github.com/Vanelfokamcode/sovereign-data-fortress

---

## Getting Started

1. **Find a model**: Use search or browse sidebar
2. **View lineage**: Click model → "Lineage" tab
3. **See code**: "Code" tab shows SQL
4. **Check tests**: "Tests" tab shows quality checks
5. **Read columns**: "Columns" tab has detailed descriptions

---

*Last updated: {{ run_started_at }}*

{% enddocs %}
