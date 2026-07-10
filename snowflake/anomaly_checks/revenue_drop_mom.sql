-- ==========================================================
-- Check 1 : Revenue Drop Month-over-Month
-- Flags months where revenue dropped by more than 30%
-- ==========================================================

WITH monthly_revenue AS (

    SELECT
        DATE_TRUNC('MONTH', d.DATE_DAY) AS month,
        SUM(f.LINE_REVENUE) AS total_revenue

    FROM RETAIL_DB.RAW_MARTS.FACT_SALES f
    JOIN RETAIL_DB.RAW_MARTS.DIM_DATE d
        ON f.DATE_ID = d.DATE_ID

    GROUP BY 1
),

with_lag AS (

    SELECT
        month,
        total_revenue,
        LAG(total_revenue) OVER(ORDER BY month) AS prev_month_revenue

    FROM monthly_revenue
)

SELECT

    month,
    total_revenue,
    prev_month_revenue,

    ROUND(
        ((total_revenue - prev_month_revenue)
        / prev_month_revenue) * 100,
        2
    ) AS pct_change

FROM with_lag

WHERE prev_month_revenue IS NOT NULL
AND ((total_revenue - prev_month_revenue)
/ prev_month_revenue) <= -0.30;