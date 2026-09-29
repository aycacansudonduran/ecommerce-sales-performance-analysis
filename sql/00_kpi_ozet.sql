-- Genel KPI özeti
-- Kapsam: teslim edilmiş siparişler, Ocak 2017 – Ağustos 2018 (20 tam ay)
-- Ciro: ürün fiyatları toplamı (kargo ücreti hariç)

WITH teslim AS (
    SELECT o.order_id,
           c.customer_unique_id,
           o.order_delivered_customer_date,
           o.order_estimated_delivery_date
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
),
siparis_tutar AS (
    SELECT order_id, SUM(price) AS tutar
    FROM order_items
    GROUP BY order_id
),
musteri_siparis AS (
    SELECT customer_unique_id, COUNT(*) AS siparis_sayisi
    FROM teslim
    GROUP BY customer_unique_id
)
SELECT
    (SELECT COUNT(*) FROM teslim)                                   AS toplam_siparis,
    (SELECT COUNT(*) FROM musteri_siparis)                          AS toplam_musteri,
    (SELECT ROUND(SUM(st.tutar), 0)
       FROM teslim t JOIN siparis_tutar st USING (order_id))        AS toplam_ciro,
    (SELECT ROUND(AVG(st.tutar), 2)
       FROM teslim t JOIN siparis_tutar st USING (order_id))        AS ort_sepet_tutari,
    (SELECT ROUND(100.0 * SUM(siparis_sayisi > 1) / COUNT(*), 2)
       FROM musteri_siparis)                                        AS tekrar_alim_orani_yuzde,
    (SELECT ROUND(100.0 * SUM(date(order_delivered_customer_date) > date(order_estimated_delivery_date))
                  / COUNT(order_delivered_customer_date), 2)
       FROM teslim)                                                 AS gec_teslimat_orani_yuzde,
    (SELECT ROUND(AVG(r.review_score), 2)
       FROM teslim t JOIN order_reviews r USING (order_id))         AS ort_musteri_puani;
