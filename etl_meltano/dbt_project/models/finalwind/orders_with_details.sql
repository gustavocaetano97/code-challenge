WITH order_details_agg AS (
    SELECT
        order_id,
        SUM(unit_price * quantity * (1 - discount)) AS total_order_value,
        COUNT(*) AS total_items_ordered
    FROM {{ ref('order_details') }}
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    od.total_order_value,
    od.total_items_ordered
FROM {{ ref('orders') }} AS o
LEFT JOIN order_details_agg AS od ON o.order_id = od.order_id;