-- Teslimat performansı ve müşteri memnuniyeti ilişkisi
-- Gecikme = gerçek teslim tarihi − tahmini teslim tarihi (gün). Negatif değer erken teslim demektir.

WITH puan AS (
    SELECT order_id, AVG(review_score) AS puan
    FROM order_reviews
    GROUP BY order_id
),
teslimat AS (
    SELECT o.order_id,
           julianday(date(o.order_delivered_customer_date))
         - julianday(date(o.order_estimated_delivery_date)) AS gecikme_gun,
           p.puan
    FROM orders o
    JOIN puan p ON p.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
),
gruplu AS (
    SELECT *,
           CASE
               WHEN gecikme_gun <= -8 THEN 1
               WHEN gecikme_gun <= 0  THEN 2
               WHEN gecikme_gun <= 3  THEN 3
               WHEN gecikme_gun <= 7  THEN 4
               WHEN gecikme_gun <= 14 THEN 5
               ELSE 6
           END AS sira
    FROM teslimat
)
SELECT
    sira,
    CASE sira
        WHEN 1 THEN '1 haftadan fazla erken'
        WHEN 2 THEN 'Zamanında (0-7 gün erken)'
        WHEN 3 THEN '1-3 gün geç'
        WHEN 4 THEN '4-7 gün geç'
        WHEN 5 THEN '8-14 gün geç'
        ELSE        '14 günden fazla geç'
    END                                                AS teslimat_durumu,
    COUNT(*)                                           AS siparis_sayisi,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS siparis_payi_yuzde,
    ROUND(AVG(puan), 2)                                AS ort_musteri_puani,
    ROUND(100.0 * AVG(puan <= 2), 1)                   AS olumsuz_yorum_yuzde
FROM gruplu
GROUP BY sira
ORDER BY sira;
