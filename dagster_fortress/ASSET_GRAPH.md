# Asset Graph Guide

## Viewing the Complete Graph

1. Open Dagster UI: `http://localhost:3000`
2. Click **"Assets"** in left menu
3. Click **"View global asset lineage"**
4. Zoom, pan, and explore!

## Graph Structure
```
┌─────────────────────────────────────────────────┐
│  INGESTION LAYER                                │
│  ├─ raw_crypto_prices (API → MinIO)            │
│  └─ resilient_raw_crypto_prices (with retries) │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  LOADING LAYER                                  │
│  └─ postgres_raw_crypto_prices (MinIO → PG)    │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  TRANSFORMATION LAYER (dbt)                     │
│  ├─ stg_crypto_prices (staging)                │
│  ├─ int_crypto_daily_aggregates (intermediate) │
│  ├─ fct_daily_crypto_prices (fact)             │
│  ├─ dim_crypto (dimension)                     │
│  └─ dim_date (dimension)                       │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  OBSERVABILITY LAYER                            │
│  ├─ pipeline_health_metrics                    │
│  └─ data_quality_score                         │
└─────────────────────────────────────────────────┘
```

## Asset Groups

- **ingestion**: Raw data extraction
- **loading**: Data movement
- **transformations**: dbt models
- **partitioned**: Time-series processing
- **observability**: Metrics & monitoring
- **documentation**: Living docs

## Graph Features

### 1. Click Any Asset
- View description
- See code
- Check metadata
- View lineage
- Run history

### 2. Search
- Type asset name
- Filter by group
- Find dependencies

### 3. Zoom & Pan
- Scroll to zoom
- Drag to pan
- Fit to screen

### 4. Materialize
- Select assets
- Click "Materialize"
- Watch in real-time

### 5. Lineage
- Upstream: What this depends on
- Downstream: What depends on this
- Full path visualization

## Common Workflows

### Debug Data Issue
1. Find problematic asset
2. Click to view details
3. Check upstream dependencies
4. Identify root cause
5. Fix and re-materialize

### Impact Analysis
1. Select asset to change
2. View downstream assets
3. Assess impact scope
4. Plan rollout

### Onboarding
1. Open global lineage
2. Follow data flow
3. Click assets to learn
4. Understand architecture

## Tips

✅ Use search for quick navigation
✅ Bookmark important asset URLs
✅ Check metadata before debugging
✅ Follow lineage for root cause
✅ Group view for organization
