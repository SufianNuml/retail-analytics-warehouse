# Data Generation Summary

Generated: 2026-06-23  
Script: scripts/generate_data.py  
Seed: Faker.seed(42), random.seed(42), np.random.seed(42)

## Row Counts (post-dirty-injection)

- customers.csv : ~1020 rows (includes ~20 duplicates)
- products.csv  : 100 rows
- stores.csv    : 15 rows
- orders.csv    : 8000 rows (includes ~120 FK violations, ~80 future dates)
- payments.csv  : ~8160 rows (includes ~160 duplicates)
- returns.csv   : ~640 rows (includes ~6 early return dates)

## Dirty Data Issues Injected

1. NULL values: ~30 null emails in customers, ~2 null prices in products  
2. Duplicates: ~20 duplicate rows in customers, ~160 in payments  
3. FK violations: ~120 orders with customer_id = CUST-GHOST-999  
4. Invalid dates: ~80 future order_dates, ~6 return_dates before order_date  
5. Category casing: ~15 product rows with inconsistent category casing  

## Notes

- All issues injected at 1–3% of rows — realistic data quality scenario  
- Quarantine folder created at `data/quarantine/` for Phase 4 use  