SELECT
    DATE_TRUNC('month', d.date_day) AS month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_orders,
    ROUND(
        SUM(CASE WHEN o.customer_id IS NULL THEN 1 ELSE 0 END)
        / COUNT(*) * 100,
        2
    ) AS null_rate_pct

FROM RETAIL_DB.RAW_STAGING.STG_ORDERS o

JOIN RETAIL_DB.RAW_MARTS.DIM_DATE d
    ON o.order_date = d.date_day

GROUP BY 1

HAVING
    SUM(CASE WHEN o.customer_id IS NULL THEN 1 ELSE 0 END)
    / COUNT(*) > 0.05;