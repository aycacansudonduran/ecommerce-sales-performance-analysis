-- Kohort analizi: müşteriler ilk alışveriş aylarına göre gruplanır,
-- sonraki aylarda kaçının tekrar alışveriş yaptığı izlenir.
-- Çıktı uzun formattadır: kohort_ay × ay_farki (pivot Python tarafında yapılır)

WITH siparis AS (
    SELECT c.customer_unique_id,
           date(o.order_purchase_timestamp, 'start of month') AS siparis_ayi
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
),
ilk_alis AS (
    SELECT customer_unique_id, MIN(siparis_ayi) AS kohort_ay
    FROM siparis
    GROUP BY customer_unique_id
),
aktivite AS (
    SELECT DISTINCT
           i.kohort_ay,
           s.customer_unique_id,
           (CAST(strftime('%Y', s.siparis_ayi) AS INTEGER) - CAST(strftime('%Y', i.kohort_ay) AS INTEGER)) * 12
         + (CAST(strftime('%m', s.siparis_ayi) AS INTEGER) - CAST(strftime('%m', i.kohort_ay) AS INTEGER)) AS ay_farki
    FROM siparis s
    JOIN ilk_alis i USING (customer_unique_id)
),
kohort_boyut AS (
    SELECT kohort_ay, COUNT(*) AS kohort_buyuklugu
    FROM ilk_alis
    GROUP BY kohort_ay
)
SELECT
    strftime('%Y-%m', a.kohort_ay)                  AS kohort_ay,
    a.ay_farki,
    COUNT(*)                                        AS aktif_musteri,
    k.kohort_buyuklugu,
    ROUND(100.0 * COUNT(*) / k.kohort_buyuklugu, 2) AS tutma_orani_yuzde
FROM aktivite a
JOIN kohort_boyut k USING (kohort_ay)
GROUP BY a.kohort_ay, a.ay_farki
ORDER BY a.kohort_ay, a.ay_farki;
