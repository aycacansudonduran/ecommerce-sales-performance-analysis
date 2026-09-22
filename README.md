# E-Ticaret Satış Performansı Analizi

Bu proje, 2 yıllık (2023-2024) bir e-ticaret satış veri seti üzerinde derinlemesine
keşifsel veri analizi (EDA) yaparak satış trendlerini, kategori/bölge/kanal
performansını ve indirim-kâr ilişkisini görselleştirmeyi amaçlamaktadır.

## Proje Özeti

170.000+ satırlık işlem verisi üzerinden iş kararlarını destekleyecek analizler
üretilmiştir: hangi ayların/günlerin ciroyu sürüklediği, hangi kategori ve
bölgelerin öne çıktığı, mobil ve web kanallarının performans farkı, müşteri
segmentlerinin ciroya katkısı ve indirim oranının kârlılığa etkisi.

## Veri Seti

Veri seti, gerçekçi mevsimsellik (Kasım kampanya dönemi, hafta sonu yoğunluğu,
yıl sonu artışı) ve iş mantığı (kategori bazlı kâr marjı, indirim davranışı)
içerecek şekilde parametrik olarak üretilmiştir (`src/generate_data.py`).

| Alan | Açıklama |
|---|---|
| Tarih | İşlem tarihi (2023-01-01 – 2024-12-31) |
| Kategori | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Spor & Outdoor, Kitap & Kırtasiye |
| Bölge | Türkiye coğrafi bölgeleri |
| Kanal | Mobil Uygulama / Web Sitesi |
| Müşteri Segmenti | Yeni / Kayıtlı / Sadık Müşteri |
| Birim Fiyat, Adet, İndirim Oranı, Net Ciro, Kâr | İşlem detayları |

## Analiz Adımları

1. **Aylık ciro trendi** — mevsimsellik ve kampanya etkisinin tespiti
2. **Kategori bazlı performans** — hangi ürün grupları ciroyu sürüklüyor
3. **Bölge x Kanal karşılaştırması** — coğrafi ve kanal bazlı performans farkları
4. **Haftalık dağılım** — hafta içi/hafta sonu satış davranışı
5. **Müşteri segmenti payı** — kayıtlı/yeni/sadık müşteri kırılımı
6. **İndirim–kâr ilişkisi** — indirim oranı arttıkça ortalama sipariş kârının değişimi

## Kullanılan Teknolojiler

- Python
- Pandas (veri işleme, gruplama)
- NumPy (sentetik veri üretimi, olasılıksal modelleme)
- Matplotlib (özel tasarım sistemi ile görselleştirme)

## Proje Yapısı

```
ecommerce-sales-performance-analysis/
├── data/                   # Üretilen veri seti (CSV)
├── src/
│   ├── generate_data.py    # Sentetik veri üretimi
│   └── analysis.py         # EDA + görselleştirme
├── outputs/                # Üretilen grafikler (PNG)
└── README.md
```

## Çalıştırma

```bash
python src/generate_data.py   # Veri setini üretir
python src/analysis.py        # Grafikleri outputs/ klasörüne kaydeder
```

## Öne Çıkan Bulgular

- Kasım ayı (Kara Cuma kampanyası), yıllık ortalamanın ~%180 üzerinde ciro üretiyor
- Elektronik kategorisi tek başına toplam cironun büyük çoğunluğunu oluşturuyor
- Mobil uygulama, web sitesine kıyasla tüm bölgelerde daha yüksek ciro üretiyor
- İndirim oranı %0'dan %21+'a çıktıkça ortalama sipariş kârı ~%30 azalıyor

## Yazar

Bu proje, veri bilimi portföyü amacıyla hazırlanmıştır.
