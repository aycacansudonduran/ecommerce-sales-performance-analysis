-- Aylık satış trendi: sipariş, müşteri, ciro ve ortalama sepet tutarı

WITH siparis_tutar AS (
    SELECT order_id, SUM(price) AS tutar
    FROM order_items
    GROUP BY order_id
)
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp)   AS ay,
    COUNT(DISTINCT o.order_id)                      AS siparis_sayisi,
    COUNT(DISTINCT c.customer_unique_id)            AS musteri_sayisi,
    ROUND(SUM(st.tutar), 2)                         AS ciro,
    ROUND(AVG(st.tutar), 2)                         AS ort_sepet_tutari
FROM orders o
JOIN customers c      ON c.customer_id = o.customer_id
JOIN siparis_tutar st ON st.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01'
GROUP BY ay
ORDER BY ay;
