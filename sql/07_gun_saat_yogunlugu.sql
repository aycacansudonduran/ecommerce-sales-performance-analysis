-- Haftanın günü × saat bazında sipariş yoğunluğu (kampanya ve bildirim zamanlaması için)
-- strftime('%w'): 0 = Pazar ... 6 = Cumartesi

SELECT
    CAST(strftime('%w', order_purchase_timestamp) AS INTEGER) AS gun_no,
    CAST(strftime('%H', order_purchase_timestamp) AS INTEGER) AS saat,
    COUNT(*)                                                  AS siparis_sayisi
FROM orders
WHERE order_status = 'delivered'
  AND order_purchase_timestamp >= '2017-01-01'
  AND order_purchase_timestamp <  '2018-09-01'
GROUP BY gun_no, saat
ORDER BY gun_no, saat;
