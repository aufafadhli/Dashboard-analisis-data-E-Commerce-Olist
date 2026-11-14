import os

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Analisis E-Commerce Olist",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AWAL_PERIODE = pd.Timestamp("2017-01-01")
AKHIR_PERIODE = pd.Timestamp("2018-09-01")  # eksklusif, jadi data sampai 31 Agustus 2018

BIRU = "#2F5D8C"
BIRU_MUDA = "#9DB7D1"
HIJAU = "#4C9A6A"
MERAH = "#C8553D"
ORANYE = "#E09F3E"
ABU = "#8A8F98"
TEKS = "#2B2F36"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#D5D8DD",
        "axes.labelcolor": TEKS,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlecolor": TEKS,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#ECEEF1",
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "xtick.color": TEKS,
        "ytick.color": TEKS,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "text.color": TEKS,
    }
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1250px;}
        h1 {font-size: 1.9rem !important; font-weight: 700 !important; letter-spacing: -0.3px;}
        h3 {font-size: 1.15rem !important; font-weight: 650 !important;}
        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,0.28);
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stMetricLabel"] p {font-size: 0.82rem; opacity: 0.75;}
        div[data-testid="stMetricValue"] {font-size: 1.55rem; font-weight: 650;}
        button[data-baseweb="tab"] {font-size: 0.95rem; padding: 0.6rem 1rem;}
        .temuan {
            border-left: 4px solid #2F5D8C;
            background: rgba(47,93,140,0.08);
            padding: 12px 16px;
            border-radius: 4px;
            margin: 8px 0 4px 0;
            font-size: 0.95rem;
            line-height: 1.55;
        }
        .temuan b {font-weight: 650;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Fungsi bantu
# ---------------------------------------------------------------------------
def angka(nilai, desimal=0):
    """Format angka dengan pemisah ribuan titik dan desimal koma."""
    teks = f"{nilai:,.{desimal}f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def ringkas(nilai):
    if nilai >= 1_000_000:
        return f"{angka(nilai / 1_000_000, 2)} juta"
    if nilai >= 1_000:
        return f"{angka(nilai / 1_000, 1)} ribu"
    return angka(nilai)


def format_ribuan(x, _pos=None):
    return f"{x / 1000:,.0f}K"


def temuan(teks):
    st.markdown(f'<div class="temuan">{teks}</div>', unsafe_allow_html=True)


def selesai(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Memuat data
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Memuat data...")
def muat_data():
    items = pd.read_csv(
        os.path.join(BASE_DIR, "main_data.csv"),
        usecols=[
            "order_id",
            "order_item_id",
            "price",
            "order_purchase_timestamp",
            "purchase_year",
            "purchase_month",
            "product_category_name_english",
        ],
        parse_dates=["order_purchase_timestamp"],
    )
    orders = pd.read_csv(
        os.path.join(BASE_DIR, "order_data.csv"),
        usecols=[
            "order_id",
            "customer_state",
            "order_purchase_timestamp",
            "purchase_month",
            "review_score",
            "is_late",
            "delay_days",
        ],
        parse_dates=["order_purchase_timestamp"],
    )
    rfm = pd.read_csv(os.path.join(BASE_DIR, "rfm_data.csv"))
    return items, orders, rfm


try:
    items_df, orders_df, rfm_df = muat_data()
except FileNotFoundError as err:
    st.error(
        f"Berkas data tidak ditemukan: {err.filename}. "
        "Pastikan main_data.csv, order_data.csv, dan rfm_data.csv "
        "berada satu folder dengan dashboard.py."
    )
    st.stop()

items_periode = items_df[
    (items_df["order_purchase_timestamp"] >= AWAL_PERIODE)
    & (items_df["order_purchase_timestamp"] < AKHIR_PERIODE)
]
orders_periode = orders_df[
    (orders_df["order_purchase_timestamp"] >= AWAL_PERIODE)
    & (orders_df["order_purchase_timestamp"] < AKHIR_PERIODE)
]
orders_review = orders_periode.dropna(subset=["review_score"]).copy()

# Ringkasan bulanan (dipakai pertanyaan 3)
bulanan = (
    items_periode.groupby("purchase_month")
    .agg(jumlah_order=("order_id", "nunique"), revenue=("price", "sum"))
    .reset_index()
)
bulanan["mom_revenue"] = bulanan["revenue"].pct_change() * 100
bulanan["mom_order"] = bulanan["jumlah_order"].pct_change() * 100


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Tentang Dashboard")
    st.write(
        "Dashboard ini merangkum hasil analisis data transaksi marketplace Olist "
        "(Brazil) untuk menjawab tiga pertanyaan bisnis."
    )
    st.markdown("**Pertanyaan bisnis**")
    st.markdown(
        "1. Kategori produk dengan revenue terbesar sepanjang 2017.\n"
        "2. Pengaruh keterlambatan terhadap review score dan state dengan "
        "keterlambatan tertinggi.\n"
        "3. Bulan puncak order dan revenue, serta pertumbuhan MoM."
    )
    st.markdown("**Cakupan data**")
    st.markdown(
        "- Hanya pesanan berstatus *delivered*\n"
        "- Pertanyaan 1: tahun 2017\n"
        "- Pertanyaan 2 dan 3: Januari 2017 sampai Agustus 2018\n"
        "- Revenue dihitung dari harga item, tanpa ongkos kirim"
    )
    st.divider()
    st.caption("Muhammad Aufa Fadhlillah Hafizh")
    st.caption("ID Dicoding: DS200B6Y1104")


# ---------------------------------------------------------------------------
# Header dan ringkasan umum
# ---------------------------------------------------------------------------
st.title("Dashboard Analisis E-Commerce Olist")
st.caption(
    "Pesanan terkirim (delivered), Januari 2017 sampai Agustus 2018. "
    "Nilai moneter dalam Brazilian Real (BRL)."
)

total_order = orders_periode["order_id"].nunique()
total_revenue = items_periode["price"].sum()
rata_review = orders_review["review_score"].mean()
persen_telat = orders_review["is_late"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total order", angka(total_order))
k2.metric("Total revenue", f"{ringkas(total_revenue)} BRL")
k3.metric("Rata-rata review score", angka(rata_review, 2))
k4.metric("Order terlambat", f"{angka(persen_telat, 2)}%")

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Kategori Produk",
        "Pengiriman dan Review",
        "Tren Penjualan",
        "Segmentasi Pelanggan",
        "Kesimpulan",
    ]
)


# ---------------------------------------------------------------------------
# Tab 1: Revenue per kategori (2017)
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Kategori produk dengan revenue terbesar pada 2017")

    items_2017 = items_df[items_df["purchase_year"] == 2017]
    revenue_kategori = (
        items_2017.groupby("product_category_name_english")
        .agg(revenue=("price", "sum"), jumlah_order=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    total_2017 = revenue_kategori["revenue"].sum()
    revenue_kategori["kontribusi"] = revenue_kategori["revenue"] / total_2017 * 100
    revenue_kategori["kumulatif"] = revenue_kategori["kontribusi"].cumsum()

    top_n = st.slider(
        "Jumlah kategori yang ditampilkan", min_value=5, max_value=15, value=10, step=1
    )
    top = revenue_kategori.head(top_n)

    kolom_a, kolom_b = st.columns([1.5, 1])

    with kolom_a:
        data = top.iloc[::-1]
        warna = [BIRU if i >= len(data) - 3 else BIRU_MUDA for i in range(len(data))]
        fig, ax = plt.subplots(figsize=(7.5, 0.42 * top_n + 1.6))
        ax.barh(data["product_category_name_english"], data["revenue"], color=warna)
        for i, (rev, pct) in enumerate(zip(data["revenue"], data["kontribusi"])):
            ax.text(
                rev,
                i,
                f"  {rev / 1000:,.0f}K ({pct:.1f}%)",
                va="center",
                fontsize=8.5,
            )
        ax.set_xlim(0, data["revenue"].max() * 1.28)
        ax.xaxis.set_major_formatter(FuncFormatter(format_ribuan))
        ax.set_xlabel("Revenue (ribu BRL)")
        ax.set_ylabel("")
        ax.grid(axis="y", visible=False)
        ax.set_title(f"{top_n} kategori dengan revenue tertinggi, 2017", loc="left")
        selesai(fig)

    with kolom_b:
        kum = revenue_kategori["kumulatif"].values
        x = np.arange(1, len(kum) + 1)
        fig, ax = plt.subplots(figsize=(5, 0.42 * top_n + 1.6))
        ax.plot(x, kum, color=BIRU, linewidth=2.2)
        ax.fill_between(x, kum, color=BIRU, alpha=0.1)
        ax.axvline(top_n, color=MERAH, linestyle="--", linewidth=1.3)
        ax.scatter([top_n], [kum[top_n - 1]], color=MERAH, zorder=3, s=40)
        ax.annotate(
            f"{kum[top_n - 1]:.1f}%",
            (top_n, kum[top_n - 1]),
            textcoords="offset points",
            xytext=(8, -14),
            color=MERAH,
            fontsize=10,
            fontweight="bold",
        )
        ax.set_ylim(0, 105)
        ax.set_xlabel("Jumlah kategori (urut dari revenue terbesar)")
        ax.set_ylabel("Kontribusi kumulatif (%)")
        ax.set_title("Konsentrasi revenue", loc="left")
        selesai(fig)

    jumlah_80 = int((revenue_kategori["kumulatif"] < 80).sum() + 1)
    tiga = top.head(3)
    nama_tiga = ", ".join(tiga["product_category_name_english"])
    temuan(
        f"Total revenue 2017 sebesar <b>{ringkas(total_2017)} BRL</b> dari "
        f"{angka(len(revenue_kategori))} kategori. {top_n} kategori teratas menyumbang "
        f"<b>{angka(top['kontribusi'].sum(), 2)}%</b>. Tiga kategori teratas adalah "
        f"{nama_tiga}, dengan kontribusi sekitar {angka(tiga['kontribusi'].min(), 1)}% "
        f"sampai {angka(tiga['kontribusi'].max(), 1)}% per kategori. "
        f"Hanya {jumlah_80} kategori yang sudah mencakup 80% revenue."
    )

    with st.expander("Lihat tabel lengkap seluruh kategori"):
        tabel = revenue_kategori.rename(
            columns={
                "product_category_name_english": "Kategori",
                "revenue": "Revenue (BRL)",
                "jumlah_order": "Jumlah order",
                "kontribusi": "Kontribusi (%)",
                "kumulatif": "Kumulatif (%)",
            }
        ).round(2)
        st.dataframe(tabel, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 2: Keterlambatan, review score, dan state
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Dampak keterlambatan terhadap review score dan sebaran per state")

    orders_review["kelompok_delay"] = pd.cut(
        orders_review["delay_days"],
        bins=[-np.inf, 0, 3, 7, np.inf],
        labels=["Tepat waktu", "Telat 1-3 hari", "Telat 4-7 hari", "Telat > 7 hari"],
    )
    review_tepat = orders_review.loc[~orders_review["is_late"], "review_score"].mean()
    review_telat = orders_review.loc[orders_review["is_late"], "review_score"].mean()
    selisih = review_tepat - review_telat

    m1, m2, m3 = st.columns(3)
    m1.metric("Review pesanan tepat waktu", angka(review_tepat, 2))
    m2.metric("Review pesanan terlambat", angka(review_telat, 2))
    m3.metric("Selisih review score", f"{angka(selisih, 2)} poin")

    kontrol_a, kontrol_b = st.columns(2)
    with kontrol_a:
        min_order = st.slider(
            "Minimal jumlah order per state",
            min_value=50,
            max_value=1000,
            value=100,
            step=50,
            help="State dengan order lebih sedikit dikeluarkan agar persentasenya tidak bias.",
        )
    with kontrol_b:
        top_state = st.slider(
            "Jumlah state yang ditampilkan", min_value=5, max_value=15, value=10, step=1
        )

    state_df = (
        orders_review.groupby("customer_state")
        .agg(
            jumlah_order=("order_id", "nunique"),
            persen_terlambat=("is_late", lambda s: s.mean() * 100),
            rata_review=("review_score", "mean"),
            rata_delay_hari=("delay_days", "mean"),
        )
        .reset_index()
    )
    state_df = state_df[state_df["jumlah_order"] >= min_order]
    state_top = state_df.sort_values("persen_terlambat", ascending=False).head(top_state)

    kolom_a, kolom_b = st.columns([1, 1.3])

    with kolom_a:
        ringkas_delay = (
            orders_review.groupby("kelompok_delay", observed=True)
            .agg(rata_review=("review_score", "mean"), jumlah=("order_id", "count"))
            .reset_index()
        )
        warna = [HIJAU, ORANYE, "#D9763C", MERAH]
        fig, ax = plt.subplots(figsize=(6, 4.6))
        batang = ax.bar(
            ringkas_delay["kelompok_delay"].astype(str),
            ringkas_delay["rata_review"],
            color=warna,
            width=0.62,
        )
        for b, n in zip(batang, ringkas_delay["jumlah"]):
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + 0.07,
                f"{b.get_height():.2f}",
                ha="center",
                fontsize=10,
                fontweight="bold",
            )
            ax.text(
                b.get_x() + b.get_width() / 2,
                0.15,
                f"n = {angka(n)}",
                ha="center",
                fontsize=8,
                color="white",
            )
        ax.set_ylim(0, 5)
        ax.set_ylabel("Rata-rata review score (1-5)")
        ax.set_title("Review score menurun seiring lamanya keterlambatan", loc="left")
        ax.tick_params(axis="x", labelsize=8.5)
        plt.setp(ax.get_xticklabels(), rotation=15)
        ax.grid(axis="x", visible=False)
        selesai(fig)

    with kolom_b:
        data = state_top.iloc[::-1]
        fig, ax = plt.subplots(figsize=(7, 4.6))
        rata_nasional = persen_telat
        warna = [MERAH if v > rata_nasional else BIRU_MUDA for v in data["persen_terlambat"]]
        ax.barh(data["customer_state"], data["persen_terlambat"], color=warna)
        for i, v in enumerate(data["persen_terlambat"]):
            ax.text(v, i, f"  {v:.1f}%", va="center", fontsize=9)
        ax.axvline(
            rata_nasional,
            color=TEKS,
            linestyle="--",
            linewidth=1,
            label=f"Rata-rata nasional {rata_nasional:.1f}%",
        )
        ax.legend(frameon=False, loc="lower right", fontsize=9)
        ax.set_xlim(0, max(data["persen_terlambat"].max(), rata_nasional) * 1.2)
        ax.set_xlabel("Persentase order terlambat (%)")
        ax.set_ylabel("")
        ax.grid(axis="y", visible=False)
        ax.set_title(f"{top_state} state dengan keterlambatan tertinggi", loc="left")
        selesai(fig)

    tiga_state = state_top.head(3)
    daftar = ", ".join(
        f"{r.customer_state} ({angka(r.persen_terlambat, 2)}%)"
        for r in tiga_state.itertuples()
    )
    temuan(
        f"Pesanan tepat waktu mendapat rata-rata review <b>{angka(review_tepat, 2)}</b>, "
        f"sedangkan pesanan terlambat <b>{angka(review_telat, 2)}</b>, selisih "
        f"<b>{angka(selisih, 2)} poin</b>. Secara keseluruhan {angka(persen_telat, 2)}% order "
        f"terlambat. Persentase keterlambatan tertinggi ada di {daftar}. "
        f"Batang merah menandai state yang berada di atas rata-rata nasional."
    )

    with st.expander("Lihat tabel state"):
        tabel = state_df.sort_values("persen_terlambat", ascending=False).rename(
            columns={
                "customer_state": "State",
                "jumlah_order": "Jumlah order",
                "persen_terlambat": "Order terlambat (%)",
                "rata_review": "Rata-rata review",
                "rata_delay_hari": "Rata-rata selisih hari",
            }
        ).round(2)
        st.dataframe(tabel, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 3: Tren bulanan
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Tren order dan revenue bulanan")

    daftar_bulan = bulanan["purchase_month"].tolist()
    kontrol_a, kontrol_b = st.columns([2, 1])
    with kontrol_a:
        awal, akhir = st.select_slider(
            "Rentang bulan",
            options=daftar_bulan,
            value=(daftar_bulan[0], daftar_bulan[-1]),
        )
    with kontrol_b:
        metrik = st.radio("Metrik", ["Revenue", "Jumlah order"], horizontal=True)

    pilih = bulanan[
        (bulanan["purchase_month"] >= awal) & (bulanan["purchase_month"] <= akhir)
    ].reset_index(drop=True)

    if metrik == "Revenue":
        kol, kol_mom, satuan = "revenue", "mom_revenue", "BRL"
    else:
        kol, kol_mom, satuan = "jumlah_order", "mom_order", "order"

    idx_puncak = pilih[kol].idxmax()
    puncak = pilih.loc[idx_puncak]
    x = np.arange(len(pilih))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1.6, 1]}
    )

    ax1.plot(x, pilih[kol], marker="o", color=BIRU, linewidth=2.3, markersize=5)
    ax1.fill_between(x, pilih[kol], color=BIRU, alpha=0.1)
    ax1.scatter(
        [idx_puncak], [puncak[kol]], color=MERAH, s=90, zorder=3, edgecolor="white", linewidth=1
    )
    teks_puncak = (
        f"Puncak: {puncak['purchase_month']}, {puncak[kol] / 1000:,.0f}K BRL"
        if metrik == "Revenue"
        else f"Puncak: {puncak['purchase_month']}, {angka(puncak[kol])} order"
    )
    ax1.annotate(
        teks_puncak,
        (idx_puncak, puncak[kol]),
        textcoords="offset points",
        xytext=(0, 14),
        ha="center",
        color=MERAH,
        fontsize=10,
        fontweight="bold",
    )
    ax1.set_ylim(0, pilih[kol].max() * 1.18)
    if metrik == "Revenue":
        ax1.yaxis.set_major_formatter(FuncFormatter(format_ribuan))
        ax1.set_ylabel("Revenue (ribu BRL)")
    else:
        ax1.set_ylabel("Jumlah order")
    ax1.set_title(f"{metrik} bulanan", loc="left")

    mom = pilih[kol_mom]
    warna = [HIJAU if (pd.notna(v) and v >= 0) else MERAH for v in mom]
    ax2.bar(x, mom.fillna(0), color=warna, width=0.65)
    ax2.axhline(0, color=TEKS, linewidth=0.9)
    for i, v in enumerate(mom):
        if pd.notna(v) and abs(v) >= 1:
            ax2.text(
                i,
                v + (3 if v >= 0 else -3),
                f"{v:.0f}%",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=7.5,
            )
    batas = mom.abs().max()
    batas = 10 if pd.isna(batas) else batas
    ax2.set_ylim(-batas * 1.25, batas * 1.25)
    ax2.set_ylabel("MoM (%)")
    ax2.set_title("Pertumbuhan month-over-month", loc="left")
    ax2.set_xticks(x)
    ax2.set_xticklabels(pilih["purchase_month"], rotation=45, ha="right")
    ax2.grid(axis="x", visible=False)
    selesai(fig)

    # Ringkasan yang selalu mengacu pada seluruh periode analisis
    puncak_order = bulanan.loc[bulanan["jumlah_order"].idxmax()]
    puncak_rev = bulanan.loc[bulanan["revenue"].idxmax()]
    temuan(
        f"Pada seluruh periode analisis, order terbanyak terjadi pada "
        f"<b>{puncak_order['purchase_month']}</b> ({angka(puncak_order['jumlah_order'])} order) "
        f"dan revenue tertinggi pada <b>{puncak_rev['purchase_month']}</b> "
        f"({angka(puncak_rev['revenue'] / 1000, 1)} ribu BRL). Pertumbuhan MoM pada bulan "
        f"puncak mencapai {angka(puncak_rev['mom_revenue'], 2)}%. Angka pada grafik "
        f"mengikuti rentang bulan dan metrik yang dipilih."
    )

    st.write("")
    st.markdown("**Pola order berdasarkan hari dan jam**")

    pola = orders_periode[
        (orders_periode["purchase_month"] >= awal)
        & (orders_periode["purchase_month"] <= akhir)
    ].copy()
    pola["hari"] = pola["order_purchase_timestamp"].dt.dayofweek
    pola["jam"] = pola["order_purchase_timestamp"].dt.hour
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    pivot = (
        pola.pivot_table(index="hari", columns="jam", values="order_id", aggfunc="count")
        .reindex(index=range(7), columns=range(24))
        .fillna(0)
    )

    kolom_a, kolom_b = st.columns([1, 1.7])
    with kolom_a:
        per_hari = pivot.sum(axis=1)
        warna = [BIRU if v == per_hari.max() else BIRU_MUDA for v in per_hari]
        fig, ax = plt.subplots(figsize=(5, 4.2))
        ax.bar(nama_hari, per_hari.values, color=warna, width=0.65)
        ax.set_ylabel("Jumlah order")
        ax.set_title("Order per hari", loc="left")
        ax.grid(axis="x", visible=False)
        plt.setp(ax.get_xticklabels(), rotation=30)
        selesai(fig)

    with kolom_b:
        fig, ax = plt.subplots(figsize=(8, 4.2))
        gambar = ax.imshow(pivot.values, aspect="auto", cmap="Blues")
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{j:02d}" for j in range(0, 24, 2)])
        ax.set_yticks(range(7))
        ax.set_yticklabels(nama_hari)
        ax.set_xlabel("Jam")
        ax.grid(False)
        ax.set_title("Intensitas order: hari dan jam", loc="left")
        batang_warna = fig.colorbar(gambar, ax=ax, pad=0.02)
        batang_warna.set_label("Jumlah order")
        batang_warna.outline.set_visible(False)
        selesai(fig)

    if per_hari.sum() > 0:
        hari_top = nama_hari[int(per_hari.idxmax())]
        hari_low = nama_hari[int(per_hari.idxmin())]
        jam_top = int(pivot.sum(axis=0).idxmax())
        persen_malam = pivot.loc[:, 0:5].values.sum() / pivot.values.sum() * 100
        temuan(
            f"Pada rentang yang dipilih, order terbanyak masuk pada hari <b>{hari_top}</b> "
            f"dan paling sedikit pada hari <b>{hari_low}</b>. Jam tersibuk adalah "
            f"<b>{jam_top:02d}.00</b>, sedangkan order pukul 00.00 sampai 05.59 hanya "
            f"{angka(persen_malam, 1)}% dari total."
        )


# ---------------------------------------------------------------------------
# Tab 4: RFM
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Segmentasi pelanggan dengan analisis RFM")
    st.write(
        "Pelanggan dikelompokkan berdasarkan `customer_unique_id` menurut tiga ukuran: "
        "**Recency** (hari sejak order terakhir), **Frequency** (jumlah order), dan "
        "**Monetary** (total pembayaran). Pengelompokan dilakukan secara manual dengan "
        "aturan skor, tanpa algoritma machine learning."
    )

    urutan_segmen = [
        "Loyal",
        "At Risk",
        "Recent Big Spender",
        "Recent Low Spender",
        "Lapsed Big Spender",
        "Lost",
    ]
    ringkasan = (
        rfm_df.groupby("segmen")
        .agg(
            jumlah_pelanggan=("customer_unique_id", "count"),
            rata_recency=("recency", "mean"),
            rata_frequency=("frequency", "mean"),
            rata_monetary=("monetary", "mean"),
        )
        .reindex(urutan_segmen)
        .dropna()
    )
    total_pelanggan = int(ringkasan["jumlah_pelanggan"].sum())
    pelanggan_ulang = int((rfm_df["frequency"] > 1).sum())

    r1, r2, r3 = st.columns(3)
    r1.metric("Pelanggan unik", angka(total_pelanggan))
    r2.metric("Pelanggan belanja lebih dari sekali", angka(pelanggan_ulang))
    r3.metric("Proporsi pembeli ulang", f"{angka(pelanggan_ulang / total_pelanggan * 100, 1)}%")

    kolom_a, kolom_b = st.columns([1.2, 1])
    with kolom_a:
        data = ringkasan.sort_values("jumlah_pelanggan")
        warna_segmen = {
            "Loyal": HIJAU,
            "At Risk": ORANYE,
            "Recent Big Spender": BIRU,
            "Recent Low Spender": BIRU_MUDA,
            "Lapsed Big Spender": "#B07AA1",
            "Lost": ABU,
        }
        fig, ax = plt.subplots(figsize=(7.5, 4.4))
        ax.barh(
            data.index,
            data["jumlah_pelanggan"],
            color=[warna_segmen[s] for s in data.index],
        )
        for i, v in enumerate(data["jumlah_pelanggan"]):
            ax.text(
                v,
                i,
                f"  {angka(v)} ({v / total_pelanggan * 100:.1f}%)",
                va="center",
                fontsize=9,
            )
        ax.set_xlim(0, data["jumlah_pelanggan"].max() * 1.3)
        ax.set_xlabel("Jumlah pelanggan")
        ax.set_ylabel("")
        ax.grid(axis="y", visible=False)
        ax.set_title("Jumlah pelanggan per segmen", loc="left")
        selesai(fig)

    with kolom_b:
        tabel = ringkasan.rename(
            columns={
                "jumlah_pelanggan": "Pelanggan",
                "rata_recency": "Recency (hari)",
                "rata_frequency": "Frequency",
                "rata_monetary": "Monetary (BRL)",
            }
        ).round(1)
        tabel.index.name = "Segmen"
        st.dataframe(tabel)
        st.caption(
            "Recency, Frequency, dan Monetary pada tabel adalah rata-rata tiap segmen."
        )

    recent = ringkasan.loc[
        [s for s in ["Recent Big Spender", "Recent Low Spender"] if s in ringkasan.index],
        "jumlah_pelanggan",
    ].sum()
    temuan(
        f"Dari {angka(total_pelanggan)} pelanggan unik, hanya "
        f"<b>{angka(pelanggan_ulang / total_pelanggan * 100, 1)}%</b> yang berbelanja lebih dari sekali. "
        f"Segmen Recent Big Spender dan Recent Low Spender berjumlah sekitar "
        f"<b>{angka(recent)}</b> pelanggan. Kelompok ini baru bertransaksi dan "
        f"menjadi sasaran utama program pembelian ulang."
    )


# ---------------------------------------------------------------------------
# Tab 5: Kesimpulan dan rekomendasi
# ---------------------------------------------------------------------------
with tab5:
    st.subheader("Kesimpulan")
    st.markdown(
        "**Pertanyaan 1 - Revenue per kategori (2017).** Revenue 2017 didominasi "
        "beberapa kategori. Sepuluh kategori teratas menyumbang 63,13% dari total revenue "
        "sekitar 5,96 juta BRL. Tiga teratas adalah bed_bath_table (8,23%), "
        "watches_gifts (7,98%), dan health_beauty (7,95%)."
    )
    st.markdown(
        "**Pertanyaan 2 - Keterlambatan dan review.** Keterlambatan berkaitan dengan "
        "review score yang lebih rendah. Rata-rata review pesanan tepat waktu 4,30 dan "
        "pesanan terlambat 2,57, selisih 1,73 poin. Secara keseluruhan 8,01% order "
        "terlambat, dengan angka tertinggi di AL (23,41%), MA (19,32%), dan PI (15,96%)."
    )
    st.markdown(
        "**Pertanyaan 3 - Tren bulanan.** Order dan revenue tertinggi terjadi pada "
        "November 2017, yaitu 7.288 order dan sekitar 987,6 ribu BRL. Revenue naik 52,36% "
        "dari Oktober, turun 26,49% pada Desember, lalu cenderung stabil sepanjang 2018 "
        "di kisaran 830 ribu sampai 977 ribu BRL per bulan."
    )
    st.markdown(
        "**Temuan tambahan - RFM.** Hanya sekitar 3% pelanggan yang berbelanja lebih "
        "dari sekali, sehingga ruang untuk meningkatkan pembelian ulang masih besar."
    )

    st.subheader("Rekomendasi")
    st.markdown(
        "1. Prioritaskan promosi dan ketersediaan stok pada kategori dengan revenue "
        "tertinggi, seperti bed_bath_table, watches_gifts, health_beauty, dan sports_leisure.\n"
        "2. Evaluasi estimasi pengiriman dan kinerja ekspedisi di state dengan keterlambatan "
        "tertinggi (AL, MA, PI, CE, dan SE).\n"
        "3. Beri informasi lebih awal atau voucher kepada pelanggan yang pesanannya "
        "terlambat untuk menekan penurunan kepuasan.\n"
        "4. Siapkan stok, gudang, dan ekspedisi sejak Oktober untuk menghadapi lonjakan "
        "order pada November.\n"
        "5. Tingkatkan pembelian ulang lewat program retensi, misalnya voucher pembelian "
        "kedua atau email tindak lanjut untuk segmen Recent Big Spender dan Recent Low Spender."
    )

st.divider()
st.caption(
    "Sumber data: Brazilian E-Commerce Public Dataset by Olist. "
    "Dianalisis pada notebook Proyek Analisis Data."
)
