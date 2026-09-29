-- Eyalet bazında ciro, teslimat süresi, gecikme oranı ve müşteri puanı

WITH siparis_tutar AS (
    SELECT order_id, SUM(price) AS tutar
    FROM order_items
    GROUP BY order_id
),
puan AS (
    SELECT order_id, AVG(review_score) AS puan
    FROM order_reviews
    GROUP BY order_id
)
SELECT
    c.customer_state                                                      AS eyalet,
    COUNT(*)                                                              AS siparis_sayisi,
    ROUND(SUM(st.tutar), 2)                                               AS ciro,
    ROUND(AVG(julianday(o.order_delivered_customer_date)
            - julianday(o.order_purchase_timestamp)), 1)                  AS ort_teslimat_gunu,
    ROUND(100.0 * AVG(date(o.order_delivered_customer_date)
                      > date(o.order_estimated_delivery_date)), 1)              AS gec_teslimat_yuzde,
    ROUND(AVG(p.puan), 2)                                                 AS ort_musteri_puani
FROM orders o
JOIN customers c      ON c.customer_id = o.customer_id
JOIN siparis_tutar st ON st.order_id = o.order_id
LEFT JOIN puan p      ON p.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01'
GROUP BY eyalet
ORDER BY ciro DESC;
