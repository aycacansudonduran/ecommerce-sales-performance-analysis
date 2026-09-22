"""
E-Ticaret Satış Performansı Analizi
Tasarım kaynağı: dataviz skill palette (kategorik + sequential mavi ölçek)
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "ecommerce_sales_2023_2024.csv")
OUT_DIR = os.path.join(BASE_DIR, "..", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- Palet (referans: dataviz skill / palette.md) ----
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

CAT_1_BLUE = "#2a78d6"
CAT_2_ORANGE = "#eb6834"
CAT_3_AQUA = "#1baf7a"
CAT_4_YELLOW = "#eda100"
CAT_5_MAGENTA = "#e87ba4"
CAT_6_GREEN = "#008300"
CATEGORICAL_ORDER = [CAT_1_BLUE, CAT_2_ORANGE, CAT_3_AQUA, CAT_4_YELLOW, CAT_5_MAGENTA, CAT_6_GREEN]

SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]

plt.rcParams.update({
    "font.family": "Segoe UI",
    "font.size": 11,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "text.color": INK_PRIMARY,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def clean_axes(ax, y_grid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(axis="both", length=0)
    if y_grid:
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
        ax.set_axisbelow(True)


def money_fmt(x, _):
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x/1_000:.0f}B"
    return f"{x:.0f}"


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["Tarih"], encoding="utf-8-sig")
    return df


def chart_monthly_trend(df, ax=None, standalone=True):
    monthly = df.groupby(pd.Grouper(key="Tarih", freq="MS"))["Net Ciro"].sum()
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly.index, monthly.values, color=CAT_1_BLUE, linewidth=2.5,
            solid_capstyle="round", zorder=3)
    ax.fill_between(monthly.index, monthly.values, color=CAT_1_BLUE, alpha=0.08, zorder=2)

    peak_idx = monthly.idxmax()
    ax.scatter([peak_idx], [monthly[peak_idx]], color=CAT_2_ORANGE, s=55, zorder=4)
    ax.annotate(f"Kasım kampanyası\n{money_fmt(monthly[peak_idx], None)} TL",
                xy=(peak_idx, monthly[peak_idx]), xytext=(-70, 18),
                textcoords="offset points", fontsize=9.5, color=INK_SECONDARY,
                arrowprops=dict(arrowstyle="-", color=INK_MUTED, lw=1))

    clean_axes(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.set_title("Aylık Net Ciro Trendi (2023-2024)", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    ax.set_ylabel("Net Ciro (TL)")
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "01_aylik_ciro_trendi.png"), dpi=200)
        plt.close(fig)


def chart_category_performance(df, ax=None, standalone=True):
    cat_rev = df.groupby("Kategori")["Net Ciro"].sum().sort_values(ascending=False)
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = [SEQ_BLUE[-1] if i == 0 else SEQ_BLUE[max(1, 5 - i)] for i in range(len(cat_rev))]
    bars = ax.barh(cat_rev.index[::-1], cat_rev.values[::-1], color=list(reversed(colors)),
                    height=0.62)
    for bar, val in zip(bars, cat_rev.values[::-1]):
        ax.text(val + cat_rev.max() * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{money_fmt(val, None)} TL", va="center", fontsize=9.5, color=INK_SECONDARY)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", length=0)
    ax.set_xticks([])
    ax.set_title("Kategori Bazlı Toplam Ciro", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "02_kategori_performansi.png"), dpi=200)
        plt.close(fig)


def chart_region_channel(df, ax=None, standalone=True):
    pivot = df.groupby(["Bölge", "Kanal"])["Net Ciro"].sum().unstack().fillna(0)
    order = pivot.sum(axis=1).sort_values(ascending=False).index
    pivot = pivot.loc[order]

    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5.5))

    channels = pivot.columns.tolist()
    x = np.arange(len(pivot))
    width = 0.36
    colors = [CAT_1_BLUE, CAT_2_ORANGE]
    for i, ch in enumerate(channels):
        offset = (i - (len(channels) - 1) / 2) * width
        ax.bar(x + offset, pivot[ch].values, width=width * 0.92, color=colors[i],
               label=ch, zorder=3)

    clean_axes(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=20, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.set_title("Bölge ve Kanal Bazlı Ciro Karşılaştırması", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "03_bolge_kanal_karsilastirma.png"), dpi=200)
        plt.close(fig)


def chart_weekday_pattern(df, ax=None, standalone=True):
    df = df.copy()
    gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    df["GünAdı"] = df["Tarih"].dt.dayofweek.map(dict(enumerate(gun_isimleri)))
    weekday_avg = df.groupby("GünAdı")["Net Ciro"].sum().reindex(gun_isimleri)

    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    max_i = weekday_avg.values.argmax()
    colors = [CAT_2_ORANGE if i == max_i else SEQ_BLUE[3] for i in range(len(weekday_avg))]
    bars = ax.bar(weekday_avg.index, weekday_avg.values, color=colors, width=0.6, zorder=3)

    clean_axes(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.set_title("Haftanın Günlerine Göre Ciro Dağılımı", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "04_haftalik_dagilim.png"), dpi=200)
        plt.close(fig)


def chart_segment_share(df, ax=None, standalone=True):
    seg = df.groupby("Müşteri Segmenti")["Net Ciro"].sum().sort_values(ascending=False)
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5.5))
    colors = CATEGORICAL_ORDER[: len(seg)]
    bars = ax.bar(seg.index, seg.values, color=colors, width=0.55, zorder=3)
    total = seg.sum()
    for bar, val in zip(bars, seg.values):
        pct = val / total * 100
        ax.text(bar.get_x() + bar.get_width() / 2, val + total * 0.01,
                f"%{pct:.0f}", ha="center", fontsize=10, color=INK_SECONDARY, fontweight="bold")

    clean_axes(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.set_title("Müşteri Segmentine Göre Ciro Payı", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "05_musteri_segmenti.png"), dpi=200)
        plt.close(fig)


def chart_discount_vs_margin(df, ax=None, standalone=True):
    bins = [-0.01, 0.0, 0.05, 0.10, 0.15, 0.20, 0.35]
    labels = ["%0", "%1-5", "%6-10", "%11-15", "%16-20", "%21+"]
    df = df.copy()
    df["İndirim Grubu"] = pd.cut(df["İndirim Oranı"], bins=bins, labels=labels)
    grp = df.groupby("İndirim Grubu", observed=True)["Kâr"].mean()

    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    colors = [SEQ_BLUE[max(1, 6 - i)] for i in range(len(grp))]
    bars = ax.bar(grp.index.astype(str), grp.values, color=colors, width=0.6, zorder=3)
    for bar, val in zip(bars, grp.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + grp.max() * 0.02,
                f"{val:.0f} TL", ha="center", fontsize=9.5, color=INK_SECONDARY)

    clean_axes(ax)
    ax.set_title("İndirim Oranına Göre Ortalama Sipariş Kârı", fontsize=14, fontweight="bold",
                 color=INK_PRIMARY, loc="left", pad=14)
    ax.set_xlabel("İndirim Grubu")
    if standalone and fig:
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, "06_indirim_kar_iliskisi.png"), dpi=200)
        plt.close(fig)


def build_dashboard(df):
    """Vitrin için tek görselde 4 panelli özet dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10.2))
    fig.suptitle("E-Ticaret Satış Performansı — 2023-2024 Özet", fontsize=17,
                 fontweight="bold", color=INK_PRIMARY, x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.935, "Python · Pandas · Matplotlib ile hazırlanmıştır",
              fontsize=10, color=INK_MUTED, ha="left")

    chart_monthly_trend(df, ax=axes[0, 0], standalone=False)
    chart_category_performance(df, ax=axes[0, 1], standalone=False)
    chart_region_channel(df, ax=axes[1, 0], standalone=False)
    chart_segment_share(df, ax=axes[1, 1], standalone=False)

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(os.path.join(OUT_DIR, "00_dashboard_vitrin.png"), dpi=200)
    plt.close(fig)


def main():
    df = load_data()
    chart_monthly_trend(df)
    chart_category_performance(df)
    chart_region_channel(df)
    chart_weekday_pattern(df)
    chart_segment_share(df)
    chart_discount_vs_margin(df)
    build_dashboard(df)
    print("Tüm grafikler outputs/ klasörüne kaydedildi.")


if __name__ == "__main__":
    main()
