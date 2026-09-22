"""
Sentetik ama gerçekçi bir e-ticaret satış veri seti üretir.
2023-01-01 - 2024-12-31 arası günlük işlem verisi.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

CATEGORIES = {
    "Elektronik": {"weight": 0.28, "price_range": (300, 12000), "margin": 0.14},
    "Giyim": {"weight": 0.22, "price_range": (80, 1200), "margin": 0.32},
    "Ev & Yaşam": {"weight": 0.18, "price_range": (50, 4000), "margin": 0.26},
    "Kozmetik": {"weight": 0.14, "price_range": (40, 900), "margin": 0.38},
    "Spor & Outdoor": {"weight": 0.10, "price_range": (100, 3500), "margin": 0.22},
    "Kitap & Kırtasiye": {"weight": 0.08, "price_range": (30, 400), "margin": 0.20},
}

REGIONS = {
    "Marmara": 0.34,
    "İç Anadolu": 0.19,
    "Ege": 0.16,
    "Akdeniz": 0.13,
    "Karadeniz": 0.10,
    "Doğu & Güneydoğu Anadolu": 0.08,
}

CHANNELS = {"Mobil Uygulama": 0.58, "Web Sitesi": 0.42}
SEGMENTS = {"Yeni Müşteri": 0.31, "Kayıtlı Müşteri": 0.45, "Sadık Müşteri": 0.24}

CAMPAIGN_MONTHS = {11: 1.85, 12: 1.55, 6: 1.25, 7: 1.15}  # Kasım kampanya + yıl sonu + yaz


def daily_seasonality_factor(date: pd.Timestamp) -> float:
    month_factor = CAMPAIGN_MONTHS.get(date.month, 1.0)
    weekday_factor = 1.25 if date.weekday() in (4, 5, 6) else 1.0  # Cuma-Cmt-Pazar
    special_days = {
        (11, 24): 2.6, (11, 25): 2.3,  # Kara Cuma haftası
        (12, 31): 1.6, (1, 1): 0.6,
    }
    special_factor = special_days.get((date.month, date.day), 1.0)
    return month_factor * weekday_factor * special_factor


def generate(start="2023-01-01", end="2024-12-31") -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="D")
    cats = list(CATEGORIES.keys())
    cat_w = np.array([CATEGORIES[c]["weight"] for c in cats])
    regions = list(REGIONS.keys())
    reg_w = np.array(list(REGIONS.values()))
    channels = list(CHANNELS.keys())
    ch_w = np.array(list(CHANNELS.values()))
    segments = list(SEGMENTS.keys())
    seg_w = np.array(list(SEGMENTS.values()))

    rows = []
    base_daily_orders = 140
    growth = np.linspace(1.0, 1.55, len(dates))  # 2 yılda organik büyüme

    for i, date in enumerate(dates):
        factor = daily_seasonality_factor(date) * growth[i]
        n_orders = RNG.poisson(base_daily_orders * factor)
        n_orders = max(n_orders, 5)

        order_cats = RNG.choice(cats, size=n_orders, p=cat_w / cat_w.sum())
        order_regions = RNG.choice(regions, size=n_orders, p=reg_w / reg_w.sum())
        order_channels = RNG.choice(channels, size=n_orders, p=ch_w / ch_w.sum())
        order_segments = RNG.choice(segments, size=n_orders, p=seg_w / seg_w.sum())

        for cat, reg, ch, seg in zip(order_cats, order_regions, order_channels, order_segments):
            lo, hi = CATEGORIES[cat]["price_range"]
            unit_price = RNG.lognormal(mean=np.log((lo + hi) / 2), sigma=0.45)
            unit_price = float(np.clip(unit_price, lo, hi))
            qty = RNG.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.2, 0.15, 0.1, 0.06, 0.04])

            discount_pct = 0.0
            if date.month in (11, 12) or date.weekday() in (5, 6):
                discount_pct = RNG.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30],
                                           p=[0.35, 0.2, 0.2, 0.13, 0.08, 0.04])
            else:
                discount_pct = RNG.choice([0, 0.05, 0.10], p=[0.7, 0.2, 0.1])

            gross_revenue = unit_price * qty
            net_revenue = gross_revenue * (1 - discount_pct)
            margin_rate = CATEGORIES[cat]["margin"]
            profit = net_revenue * margin_rate

            rows.append((
                date, cat, reg, ch, seg,
                round(unit_price, 2), int(qty), round(discount_pct, 2),
                round(net_revenue, 2), round(profit, 2),
            ))

    df = pd.DataFrame(rows, columns=[
        "Tarih", "Kategori", "Bölge", "Kanal", "Müşteri Segmenti",
        "Birim Fiyat", "Adet", "İndirim Oranı", "Net Ciro", "Kâr",
    ])
    return df


if __name__ == "__main__":
    import os
    df = generate()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_dir, "..", "data", "ecommerce_sales_2023_2024.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"{len(df):,} satır üretildi -> {out_path}")
    print(df.head())
