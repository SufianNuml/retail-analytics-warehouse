-- ==========================================================
-- Check 2 : Return Rate Spike
-- Flags months where return rate exceeds 1.5x
-- the trailing 3-month average.
-- ==========================================================

WITH monthly_orders AS (

    SELECT
        DATE_TRUNC('MONTH', d.DATE_DAY) AS month,
        COUNT(DISTINCT f.ORDER_ID) AS order_count

    FROM RETAIL_DB.RAW_MARTS.FACT_SALES f
    JOIN RETAIL_DB.RAW_MARTS.DIM_DATE d
        ON f.DATE_ID = d.DATE_ID

    GROUP BY 1
),

monthly_returns AS (

    SELECT
        DATE_TRUNC('MONTH', d.DATE_DAY) AS month,
        COUNT(*) AS return_count

    FROM RETAIL_DB.RAW_MARTS.FACT_RETURNS r
    JOIN RETAIL_DB.RAW_MARTS.DIM_DATE d
        ON r.DATE_ID = d.DATE_ID

    GROUP BY 1
),

combined AS (

    SELECT
        o.month,
        o.order_count,
        COALESCE(r.return_count,0) AS return_count,
        COALESCE(r.return_count,0) / NULLIF(o.order_count,0) AS return_rate

    FROM monthly_orders o
    LEFT JOIN monthly_returns r
        ON o.month = r.month
),

with_trailing_avg AS (

    SELECT
        month,
        return_rate,

        AVG(return_rate) OVER(

            ORDER BY month

            ROWS BETWEEN 3 PRECEDING
            AND 1 PRECEDING

        ) AS trailing_avg_rate

    FROM combined
)

SELECT *

FROM with_trailing_avg

WHERE trailing_avg_rate IS NOT NULL
AND return_rate > trailing_avg_rate * 1.5;