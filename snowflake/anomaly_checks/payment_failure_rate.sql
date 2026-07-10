-- ==========================================================
-- Check 3 : Payment Failure Rate
-- Flags if failed payments exceed 10% of all payments.
-- ==========================================================

SELECT

    COUNT(*) AS total_payments,

    SUM(
        CASE
            WHEN LOWER(PAYMENT_STATUS) = 'failed'
            THEN 1
            ELSE 0
        END
    ) AS failed_payments,

    ROUND(

        SUM(
            CASE
                WHEN LOWER(PAYMENT_STATUS)='failed'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),

        2

    ) AS failure_rate_pct

FROM RETAIL_DB.RAW_STAGING.STG_PAYMENTS

HAVING

SUM(
    CASE
        WHEN LOWER(PAYMENT_STATUS)='failed'
        THEN 1
        ELSE 0
    END
) * 1.0 / COUNT(*) > 0.10;