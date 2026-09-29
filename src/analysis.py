"""
E-Ticaret Satış ve Müşteri Analizi (Olist, Ocak 2017 – Ağustos 2018)

Akış: sql/*.sql sorguları SQLite veritabanında çalıştırılır ->
      sonuçlar outputs/tables/ altına CSV olarak kaydedilir (Power BI kaynağı) ->
      grafikler outputs/ altına PNG olarak kaydedilir.

Önce: python src/load_data.py
Sonra: python src/analysis.py

Tasarım kaynağı: dataviz skill palette (kategorik + sequential mavi ölçek)
"""
import os
import sqlite3

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "olist.db")
SQL_DIR = os.path.join(BASE_DIR, "..", "sql")
OUT_DIR = os.path.join(BASE_DIR, "..", "outputs")
TABLE_DIR = os.path.join(OUT_DIR, "tables")
os.makedirs(TABLE_DIR, exist_ok=True)

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

SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]
SEQ_CMAP = LinearSegmentedColormap.from_list("seq_blue", [SURFACE] + SEQ_BLUE)

plt.rcParams.update({
    "font.family": ["Segoe UI", "Segoe UI Symbol"],
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

# Grafiklerde gösterilen kategoriler için Türkçe adlar
CATEGORY_TR = {
    "health_beauty": "Sağlık & Güzellik",
    "watches_gifts": "Saat & Hediye",
    "bed_bath_table": "Ev Tekstili",
    "sports_leisure": "Spor & Hobi",
    "computers_accessories": "Bilgisayar Aksesuarı",
    "furniture_decor": "Mobilya & Dekorasyon",
    "housewares": "Ev Gereçleri",
    "cool_stuff": "Hediyelik Ürünler",
    "auto": "Otomotiv",
    "garden_tools": "Bahçe Aletleri",
    "toys": "Oyuncak",
    "baby": "Bebek",
    "perfumery": "Parfüm",
    "telephony": "Telefon",
    "office_furniture": "Ofis Mobilyası",
}

STATE_TR = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Minas Gerais",
    "RS": "Rio Grande do Sul", "PR": "Paraná", "SC": "Santa Catarina",
    "BA": "Bahia", "DF": "Distrito Federal", "GO": "Goiás", "ES": "Espírito Santo",
    "PE": "Pernambuco", "CE": "Ceará",
}

DAYS_TR = ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]
MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


# ------------------------------------------------------------------ yardımcılar

def clean_axes(ax, y_grid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(axis="both", length=0)
    if y_grid:
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
        ax.set_axisbelow(True)


def bare_axes(ax):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="both", length=0)


def money_fmt(x, _=None):
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x/1_000:.0f}B"
    return f"{x:.0f}"


def set_title(ax, title, subtitle=None):
    ax.set_title(title, fontsize=14, fontweight="bold", color=INK_PRIMARY, loc="left",
                 pad=26 if subtitle else 14)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5, color=INK_MUTED,
                va="bottom")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, name), dpi=200)
    plt.close(fig)


def run_query(conn, name):
    """sql/<name>.sql dosyasını çalıştırır, sonucu outputs/tables/<name>.csv olarak da kaydeder."""
    with open(os.path.join(SQL_DIR, f"{name}.sql"), encoding="utf-8") as f:
        df = pd.read_sql(f.read(), conn)
    df.to_csv(os.path.join(TABLE_DIR, f"{name}.csv"), index=False, encoding="utf-8-sig")
    return df


def load_all():
    if not os.path.exists(DB_PATH):
        raise SystemExit("Veritabanı bulunamadı. Önce çalıştırın: python src/load_data.py")
    names = ["00_kpi_ozet", "01_aylik_satis", "02_kategori_performansi",
             "03_eyalet_performansi", "04_rfm_segmentasyonu", "05_kohort_analizi",
             "06_teslimat_memnuniyet", "07_gun_saat_yogunlugu"]
    with sqlite3.connect(DB_PATH) as conn:
        return {name[3:]: run_query(conn, name) for name in names}


# ------------------------------------------------------------------ grafikler

def chart_monthly_trend(monthly, ax=None):
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 5))
    dates = pd.to_datetime(monthly["ay"])
    ax.plot(dates, monthly["ciro"], color=CAT_1_BLUE, linewidth=2.5,
            solid_capstyle="round", zorder=3)
    ax.fill_between(dates, monthly["ciro"], color=CAT_1_BLUE, alpha=0.08, zorder=2)

    peak = monthly["ciro"].idxmax()
    ax.scatter([dates[peak]], [monthly["ciro"][peak]], color=CAT_2_ORANGE, s=55, zorder=4)
    ax.annotate(f"Kasım 2017 · Black Friday\nR$ {money_fmt(monthly['ciro'][peak])}",
                xy=(dates[peak], monthly["ciro"][peak]), xytext=(-165, 10),
                textcoords="offset points", fontsize=9.5, color=INK_SECONDARY,
                arrowprops=dict(arrowstyle="-", color=INK_MUTED, lw=1))

    clean_axes(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{MONTHS_TR[mdates.num2date(x).month - 1]} {mdates.num2date(x):%y}"))
    ax.set_ylim(0, monthly["ciro"].max() * 1.3)
    ax.set_ylabel("Ciro (R$)")
    set_title(ax, "Aylık Ciro Trendi", "Teslim edilen siparişler, kargo hariç ürün cirosu")
    if fig:
        save(fig, "01_aylik_ciro_trendi.png")


def chart_category_performance(category, ax=None, top_n=10):
    top = category[category["kategori"] != "unknown"].head(top_n)
    labels = [CATEGORY_TR.get(k, k) for k in top["kategori"]]
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5.8))
    colors = [SEQ_BLUE[-1] if i < 3 else SEQ_BLUE[2] for i in range(len(top))]
    bars = ax.barh(labels[::-1], top["ciro"].values[::-1], color=colors[::-1], height=0.62)
    for bar, (_, row) in zip(bars, top[::-1].iterrows()):
        ax.text(bar.get_width() + top["ciro"].max() * 0.015, bar.get_y() + bar.get_height() / 2,
                f"R$ {money_fmt(row['ciro'])}  ·  %{row['ciro_payi_yuzde']:.1f}  ·  ★ {row['ort_musteri_puani']:.2f}",
                va="center", fontsize=9.5, color=INK_SECONDARY)
    bare_axes(ax)
    ax.set_xticks([])
    ax.set_xlim(0, top["ciro"].max() * 1.45)
    ax.tick_params(axis="y", colors=INK_SECONDARY)
    set_title(ax, f"En Çok Ciro Getiren {top_n} Kategori",
              "Ciro · toplam ciro payı · ortalama müşteri puanı")
    if fig:
        save(fig, "02_kategori_performansi.png")


def chart_state_delivery(state, ax=None, top_n=12):
    top = state.head(top_n).sort_values("gec_teslimat_yuzde")
    labels = [f"{STATE_TR.get(s, s)} ({s})" for s in top["eyalet"]]
    avg = (state["gec_teslimat_yuzde"] * state["siparis_sayisi"]).sum() / state["siparis_sayisi"].sum()
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    colors = [CAT_2_ORANGE if v > 10 else SEQ_BLUE[2] for v in top["gec_teslimat_yuzde"]]
    bars = ax.barh(labels, top["gec_teslimat_yuzde"], color=colors, height=0.62)
    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 0.25, bar.get_y() + bar.get_height() / 2,
                f"%{row['gec_teslimat_yuzde']:.1f}  ·  ort. {row['ort_teslimat_gunu']:.0f} gün",
                va="center", fontsize=9.5, color=INK_SECONDARY, zorder=3,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1))
    ax.axvline(avg, color=INK_MUTED, linewidth=1, linestyle="--", zorder=1)
    ax.text(avg, -0.75, f" genel ort. %{avg:.1f}", fontsize=9, color=INK_MUTED, va="top")
    bare_axes(ax)
    ax.set_xticks([])
    ax.set_xlim(0, top["gec_teslimat_yuzde"].max() * 1.55)
    ax.tick_params(axis="y", colors=INK_SECONDARY)
    set_title(ax, "Eyaletlere Göre Geç Teslimat Oranı",
              f"En çok sipariş veren {top_n} eyalet · turuncu: %10'un üzerinde gecikme")
    if fig:
        save(fig, "03_eyalet_teslimat_performansi.png")


def chart_weekday_hour(heat, ax=None):
    pivot = heat.pivot(index="gun_no", columns="saat", values="siparis_sayisi").fillna(0)
    order = [1, 2, 3, 4, 5, 6, 0]  # Pazartesi'den başlat
    pivot = pivot.loc[order]
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 4.6))
    im = ax.imshow(pivot.values, aspect="auto", cmap=SEQ_CMAP)
    ax.set_yticks(range(7))
    ax.set_yticklabels([DAYS_TR[d] for d in order], color=INK_SECONDARY)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
    bare_axes(ax)
    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(length=0, colors=INK_MUTED, labelsize=9)
    set_title(ax, "Sipariş Yoğunluğu: Gün × Saat",
              "Hafta içi 10:00–22:00 arası yoğun, Pazar akşamları da güçlü; en sakin gün Cumartesi")
    if fig:
        save(fig, "04_gun_saat_yogunlugu.png")


def chart_rfm_segments(rfm, ax=None):
    data = rfm.sort_values("ciro_payi_yuzde")
    y = np.arange(len(data))
    h = 0.36
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(10.5, 6))
    ax.barh(y + h / 2 + 0.02, data["musteri_payi_yuzde"], height=h, color=SEQ_BLUE[1],
            label="Müşteri payı")
    ax.barh(y - h / 2 - 0.02, data["ciro_payi_yuzde"], height=h, color=SEQ_BLUE[-1],
            label="Ciro payı")
    for i, (_, row) in enumerate(data.iterrows()):
        ax.text(row["musteri_payi_yuzde"] + 0.4, i + h / 2 + 0.02, f"%{row['musteri_payi_yuzde']:.1f}",
                va="center", fontsize=9, color=INK_MUTED)
        ax.text(row["ciro_payi_yuzde"] + 0.4, i - h / 2 - 0.02,
                f"%{row['ciro_payi_yuzde']:.1f}  ·  {row['musteri_sayisi']:,} müşteri".replace(",", "."),
                va="center", fontsize=9, color=INK_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels(data["segment"], color=INK_SECONDARY)
    bare_axes(ax)
    ax.set_xticks([])
    ax.set_xlim(0, data[["musteri_payi_yuzde", "ciro_payi_yuzde"]].values.max() * 1.45)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5, labelcolor=INK_SECONDARY)
    set_title(ax, "RFM Müşteri Segmentleri",
              "Her segmentin müşteri sayısındaki ve cirodaki payı")
    if fig:
        save(fig, "05_rfm_segmentleri.png")


def chart_cohort(cohort, ax=None, max_offset=12):
    pivot = cohort.pivot(index="kohort_ay", columns="ay_farki", values="tutma_orani_yuzde")
    pivot = pivot.loc[:, 1:max_offset]
    pivot = pivot[pivot.index <= "2018-02"]  # en az 6 ay izlenebilen kohortlar
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6.5))
    im = ax.imshow(pivot.values, aspect="auto", cmap=SEQ_CMAP, vmin=0, vmax=0.8)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                        color=SURFACE if v > 0.5 else INK_SECONDARY)
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels([f"{m}. ay" for m in pivot.columns])
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, color=INK_SECONDARY)
    ax.set_ylabel("İlk alışveriş ayı (kohort)")
    bare_axes(ax)
    set_title(ax, "Kohort Analizi: Müşteri Tutma Oranı (%)",
              "İlk alışverişten sonraki aylarda tekrar alışveriş yapan müşteri yüzdesi · hiçbir kohort %1'i geçmiyor")
    if fig:
        save(fig, "06_kohort_analizi.png")


def chart_delivery_satisfaction(delivery, ax=None):
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 5.2))
    labels = (delivery["teslimat_durumu"]
              .str.replace(" (", "\n(", regex=False)
              .str.replace("haftadan fazla", "haftadan\nfazla", regex=False)
              .str.replace("günden fazla", "günden\nfazla", regex=False))
    colors = [SEQ_BLUE[2] if s <= 2 else CAT_2_ORANGE for s in delivery["sira"]]
    bars = ax.bar(labels, delivery["olumsuz_yorum_yuzde"], color=colors, width=0.6)
    for bar, (_, row) in zip(bars, delivery.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"%{row['olumsuz_yorum_yuzde']:.0f}", ha="center", fontsize=11,
                fontweight="bold", color=INK_PRIMARY)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 7.5,
                f"★ {row['ort_musteri_puani']:.2f}", ha="center", fontsize=9, color=INK_MUTED)
    clean_axes(ax)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"%{v:.0f}"))
    ax.tick_params(axis="x", colors=INK_SECONDARY, labelsize=9.5)
    ax.set_ylabel("1-2 yıldızlı yorum oranı")
    set_title(ax, "Teslimat Gecikmesi Müşteri Memnuniyetini Nasıl Etkiliyor?",
              "Tahmini tarihe göre teslim durumu · çubuk: olumsuz (1-2★) yorum oranı · üstte: ortalama puan")
    if fig:
        save(fig, "07_teslimat_memnuniyet.png")


def build_dashboard(d):
    kpi = d["kpi_ozet"].iloc[0]
    fig = plt.figure(figsize=(17, 11.5))
    gs = fig.add_gridspec(3, 2, height_ratios=[0.34, 1, 1], hspace=0.55, wspace=0.36,
                          left=0.135, right=0.98, top=0.9, bottom=0.05)
    fig.suptitle("E-Ticaret Satış ve Müşteri Analizi", fontsize=22, fontweight="bold",
                 color=INK_PRIMARY, x=0.135, ha="left", y=0.975)
    fig.text(0.135, 0.935, "Olist · Brezilya · Ocak 2017 – Ağustos 2018 · SQL + Python",
             fontsize=12, color=INK_MUTED, ha="left")

    tiles = [
        ("Toplam Ciro", f"R$ {kpi['toplam_ciro'] / 1e6:.1f}M"),
        ("Sipariş", f"{int(kpi['toplam_siparis']):,}".replace(",", ".")),
        ("Ort. Sepet", f"R$ {kpi['ort_sepet_tutari']:.0f}"),
        ("Tekrar Alım", f"%{kpi['tekrar_alim_orani_yuzde']:.1f}"),
        ("Geç Teslimat", f"%{kpi['gec_teslimat_orani_yuzde']:.1f}"),
        ("Müşteri Puanı", f"★ {kpi['ort_musteri_puani']:.2f}"),
    ]
    tile_gs = gs[0, :].subgridspec(1, len(tiles), wspace=0.08)
    for i, (label, value) in enumerate(tiles):
        ax = fig.add_subplot(tile_gs[0, i])
        ax.set_facecolor("#f3f2ee")
        bare_axes(ax)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.08, 0.68, label, transform=ax.transAxes, fontsize=11, color=INK_SECONDARY)
        ax.text(0.08, 0.22, value, transform=ax.transAxes, fontsize=21, fontweight="bold",
                color=CAT_2_ORANGE if label == "Tekrar Alım" else INK_PRIMARY)

    chart_monthly_trend(d["aylik_satis"], ax=fig.add_subplot(gs[1, 0]))
    chart_delivery_satisfaction(d["teslimat_memnuniyet"], ax=fig.add_subplot(gs[1, 1]))
    chart_rfm_segments(d["rfm_segmentasyonu"], ax=fig.add_subplot(gs[2, 0]))
    chart_state_delivery(d["eyalet_performansi"], ax=fig.add_subplot(gs[2, 1]), top_n=8)

    fig.savefig(os.path.join(OUT_DIR, "00_dashboard_vitrin.png"), dpi=200)
    plt.close(fig)


def main():
    d = load_all()
    chart_monthly_trend(d["aylik_satis"])
    chart_category_performance(d["kategori_performansi"])
    chart_state_delivery(d["eyalet_performansi"])
    chart_weekday_hour(d["gun_saat_yogunlugu"])
    chart_rfm_segments(d["rfm_segmentasyonu"])
    chart_cohort(d["kohort_analizi"])
    chart_delivery_satisfaction(d["teslimat_memnuniyet"])
    build_dashboard(d)
    print(f"Grafikler: {os.path.normpath(OUT_DIR)}")
    print(f"Tablolar : {os.path.normpath(TABLE_DIR)}")


if __name__ == "__main__":
    main()
