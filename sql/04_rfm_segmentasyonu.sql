-- RFM müşteri segmentasyonu
--   Recency   : son alışverişten bu yana geçen gün (analiz tarihi = son sipariş + 1 gün)
--   Frequency : teslim edilmiş sipariş sayısı
--   Monetary  : toplam harcama (kargo hariç)
-- Müşterilerin ~%97'si tek sipariş verdiği için F puanı 5'li dilimlere bölünmez;
-- "1 sipariş" ve "2+ sipariş" olarak iki gruba ayrılır. R ve M 5'li dilimlerle (NTILE) puanlanır.

WITH siparis AS (
    SELECT c.customer_unique_id,
           o.order_id,
           o.order_purchase_timestamp,
           SUM(oi.price) AS tutar
    FROM orders o
    JOIN customers c    ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY c.customer_unique_id, o.order_id, o.order_purchase_timestamp
),
analiz_tarihi AS (
    SELECT date(MAX(order_purchase_timestamp), '+1 day') AS tarih FROM siparis
),
rfm AS (
    SELECT s.customer_unique_id,
           CAST(julianday(a.tarih) - julianday(MAX(s.order_purchase_timestamp)) AS INTEGER) AS recency,
           COUNT(*)     AS frequency,
           SUM(s.tutar) AS monetary
    FROM siparis s CROSS JOIN analiz_tarihi a
    GROUP BY s.customer_unique_id
),
puanli AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency DESC) AS r_puan,   -- 5 = en yeni
           NTILE(5) OVER (ORDER BY monetary)     AS m_puan,   -- 5 = en çok harcayan
           CASE WHEN frequency > 1 THEN 2 ELSE 1 END AS f_grup
    FROM rfm
),
segmentli AS (
    SELECT *,
           CASE
               WHEN f_grup = 2 AND r_puan >= 4  THEN 'Şampiyonlar'
               WHEN f_grup = 2                  THEN 'Sadık - İlgi Bekleyen'
               WHEN r_puan >= 4 AND m_puan >= 4 THEN 'Yeni - Yüksek Değerli'
               WHEN r_puan >= 4                 THEN 'Yeni Müşteriler'
               WHEN r_puan = 3                  THEN 'Uykuya Geçen'
               WHEN m_puan >= 4                 THEN 'Kaybedilmek Üzere (Değerli)'
               ELSE                                  'Kayıp'
           END AS segment
    FROM puanli
)
SELECT
    segment,
    COUNT(*)                                                     AS musteri_sayisi,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)           AS musteri_payi_yuzde,
    ROUND(SUM(monetary), 2)                                      AS ciro,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS ciro_payi_yuzde,
    ROUND(AVG(recency), 0)                                       AS ort_recency_gun,
    ROUND(AVG(frequency), 2)                                     AS ort_siparis_sayisi,
    ROUND(AVG(monetary), 2)                                      AS ort_harcama
FROM segmentli
GROUP BY segment
ORDER BY ciro DESC;
