-- Kategori performansı: ciro, sipariş, ortalama fiyat ve müşteri puanı
-- Aynı siparişte birden fazla kategori olabilir; puan sipariş bazında eşleştirilir.

WITH kalem AS (
    SELECT oi.order_id,
           COALESCE(t.product_category_name_english, 'unknown') AS kategori,
           oi.price
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
),
puan AS (
    SELECT order_id, AVG(review_score) AS puan
    FROM order_reviews
    GROUP BY order_id
)
SELECT
    k.kategori,
    COUNT(DISTINCT k.order_id)                                   AS siparis_sayisi,
    ROUND(SUM(k.price), 2)                                       AS ciro,
    ROUND(100.0 * SUM(k.price) / SUM(SUM(k.price)) OVER (), 2)   AS ciro_payi_yuzde,
    ROUND(AVG(k.price), 2)                                       AS ort_urun_fiyati,
    ROUND(AVG(p.puan), 2)                                        AS ort_musteri_puani
FROM kalem k
LEFT JOIN puan p ON p.order_id = k.order_id
GROUP BY k.kategori
ORDER BY ciro DESC;
