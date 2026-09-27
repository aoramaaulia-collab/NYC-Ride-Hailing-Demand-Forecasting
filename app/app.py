"""
Permintaan Ride-Hailing: dashboard dan perkiraan.

Membaca data yang disiapkan oleh siapkan_data_app.py. Tidak melatih model.
Menjalankan dari folder project:  streamlit run app/app.py
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"
W = {"utama": "#1F4E5A", "tengah": "#4A8C8F", "muda": "#86B7B4", "lyft": "#A9CFCB", "nyata": "#1C2B2D",
     "rentang": "#1F4E5A", "naik": "#2E7D4F", "turun": "#B3261E"}
MODEL_WARNA = alt.Scale(domain=["7 hari", "14 hari", "28 hari"], range=[W["utama"], W["tengah"], W["muda"]])
MODEL_GARIS = alt.Scale(domain=["7 hari", "14 hari", "28 hari"], range=[[1, 0], [1, 0], [6, 4]])
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
BULAN_PANJANG = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
                 "September", "Oktober", "November", "Desember"]

st.set_page_config(page_title="Permintaan Ride-Hailing", page_icon="🚕", layout="wide")
AKSEN = ["#1F5F6B", "#2E8C85", "#3D6FA8", "#C9892B", "#7B5A93"]   # teal, hijau laut, biru, kuning tua, ungu
st.markdown("""<style>
.block-container { padding-top: 3.4rem; max-width: 1440px; }
/* Spanduk judul */
.hero { background: linear-gradient(120deg, #123B45 0%, #1F5F6B 48%, #2E8C85 100%); border-radius: 20px;
        padding: 30px 36px 26px; box-shadow: 0 12px 32px rgba(18, 59, 69, 0.18); margin-bottom: 18px; }
.hero h1 { color: #FFFFFF !important; font-size: 2.4rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.5px; }
.hero p { color: #D6EEEA; font-size: 1.05rem; margin: 8px 0 16px; }
.pill { display: inline-block; background: rgba(255, 255, 255, 0.14); border: 1px solid rgba(255, 255, 255, 0.28);
        color: #FFFFFF; border-radius: 999px; padding: 5px 14px; margin: 0 8px 6px 0; font-size: 0.88rem; font-weight: 600; }
/* Tab berbentuk tombol */
[data-testid="stTabs"] [role="tablist"] { gap: 6px; background: #EFF6F5; padding: 6px; border-radius: 14px; border: none; }
[data-testid="stTabs"] [role="tab"] { border-radius: 10px; padding: 8px 18px; font-weight: 600; color: #35535A;
                                     transition: background 0.15s ease; }
[data-testid="stTabs"] [role="tab"]:hover { background: #DCEDEA; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background: #1F5F6B; color: #FFFFFF; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] * { color: #FFFFFF !important; }
/* Judul bagian */
h3 { color: #1F4E5A !important; font-weight: 750 !important; border-left: 5px solid #2E8C85; padding-left: 12px !important; }
h4 { color: #1F4E5A !important; }
/* Kartu */
[class*="st-key-kartu"] { background: #FFFFFF; border: 1px solid #E2ECEA; border-radius: 18px;
                          box-shadow: 0 4px 20px rgba(31, 78, 90, 0.07); padding: 20px 22px 14px; }
/* Kartu angka dengan garis warna */
[class*="st-key-kpi"] { background: #FFFFFF; border: 1px solid #E2ECEA; border-radius: 16px; padding: 14px 18px 10px;
                        box-shadow: 0 3px 14px rgba(31, 78, 90, 0.06); border-top: 5px solid var(--aksen, #1F5F6B);
                        min-height: 168px; }
[class*="st-key-kpi0"] { --aksen: #1F5F6B; } [class*="st-key-kpi1"] { --aksen: #2E8C85; }
[class*="st-key-kpi2"] { --aksen: #3D6FA8; } [class*="st-key-kpi3"] { --aksen: #C9892B; }
[class*="st-key-kpi4"] { --aksen: #7B5A93; }
[data-testid="stMetricLabel"] p { color: #56676A; font-weight: 600; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { white-space: normal !important; overflow: visible !important;
                                                                  text-overflow: clip !important; }
[data-testid="stMetricValue"] { color: #123B45; font-weight: 750; font-variant-numeric: tabular-nums;
                                font-size: clamp(1.35rem, 2.1vw, 2.05rem) !important; line-height: 1.2; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { white-space: normal !important; overflow: visible !important;
                                                                  text-overflow: clip !important; }
[data-testid="stMetricLabel"] p { font-size: 0.86rem !important; }
/* Panduan */
.langkah { display: flex; gap: 12px; align-items: flex-start; margin: 10px 0; color: #24383C; line-height: 1.5; }
.nomor { flex: 0 0 28px; height: 28px; border-radius: 50%; background: #2E8C85; color: #FFFFFF; font-weight: 700;
         display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }
</style>""", unsafe_allow_html=True)

_urut = [0]


def kartu():
    # Kartu putih berbayang; gayanya dari CSS kunci st-key-kartu
    _urut[0] += 1
    return st.container(key=f"kartu_{_urut[0]}")


def kpi_kartu(i):
    # Kartu angka dengan garis warna ke-i
    _urut[0] += 1
    return st.container(key=f"kpi{i % len(AKSEN)}_{_urut[0]}")


def panduan(langkah, judul="Cara menggunakan"):
    with st.expander(judul, expanded=True, icon=":material/help:"):
        st.markdown("".join(f'<div class="langkah"><div class="nomor">{i}</div><div>{t}</div></div>'
                            for i, t in enumerate(langkah, 1)), unsafe_allow_html=True)


# ================================================================
# Format angka Indonesia
# ================================================================
def des(v, n=1):
    return f"{v:,.{n}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def ribu(v):
    return f"{v:,.0f}".replace(",", ".")


def singkat(v, n=1):
    # Jutaan disingkat "63,3 juta"; di bawah sejuta ditulis lengkap "31.601"
    return f"{des(v / 1e6, n)} juta" if abs(v) >= 1e6 else ribu(v)


def rentang_singkat(lo, hi, n=2):
    if lo >= 1e6 and hi >= 1e6:
        return f"{des(lo / 1e6, n)}–{des(hi / 1e6, n)} juta"
    return f"{ribu(lo)}–{ribu(hi)}"


def persen(v, n=1):
    return ("+" if v > 0 else "−" if v < 0 else "") + des(abs(v), n) + "%"


def ubah(v, n=1):
    # Untuk delta st.metric: Streamlit hanya mengenali "-" biasa sebagai turun (merah)
    return ("+" if v > 0 else "-" if v < 0 else "") + des(abs(v), n) + "%"


def tgl(t, hari=True, pendek=False):
    b = BULAN if pendek else BULAN_PANJANG
    return (f"{HARI[t.dayofweek]}, " if hari else "") + f"{t.day} {b[t.month - 1]} {t.year}"


def label_bulan(bulan_list):
    # Label ringkas untuk daftar bulan berurutan, misalnya "Jan–Mei 2026" atau "2025"
    b = sorted(pd.Timestamp(x) for x in bulan_list)
    if len(b) == 12 and b[0].year == b[-1].year:
        return str(b[0].year)
    if b[0].year == b[-1].year:
        return f"{BULAN[b[0].month - 1]}–{BULAN[b[-1].month - 1]} {b[0].year}"
    return f"{BULAN[b[0].month - 1]} {b[0].year} – {BULAN[b[-1].month - 1]} {b[-1].year}"


def tabel(df, ribuan=(), desimal=None, persen_kol=None):
    # Tabel dengan pemisah ribuan titik dan desimal koma
    f = {c: ribu for c in ribuan}
    f |= {c: (lambda v, n=n: des(v, n)) for c, n in (desimal or {}).items()}
    f |= {c: (lambda v, n=n: des(v, n) + "%") for c, n in (persen_kol or {}).items()}
    return df.style.format(f, na_rep="-")


ANGKA_EXPR = "replace(format(datum.value, ',.0f'), regexp(',', 'g'), '.')"
BULAN_EXPR = ("['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][month(datum.value)]"
              " + ' ' + year(datum.value)")
TANGGAL_EXPR = "date(datum.value) + ' ' + ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][month(datum.value)]"


def sumbu_angka(judul):
    return alt.Axis(title=judul, labelExpr=ANGKA_EXPR)


def sumbu_bulan(n_bulan):
    langkah = 1 if n_bulan <= 12 else 3
    return alt.Axis(labelExpr=BULAN_EXPR, tickCount=alt.TimeIntervalStep(interval="month", step=langkah))


def sumbu_tanggal(n_hari):
    langkah = max(1, round(n_hari / 14))
    return alt.Axis(labelExpr=TANGGAL_EXPR, tickCount=alt.TimeIntervalStep(interval="day", step=langkah))


def siapkan_tooltip(df, kolom_waktu, per_jam=False):
    # Kolom teks untuk tooltip: tanggal Indonesia dan angka bulat
    d = df.copy()
    d["Waktu"] = d[kolom_waktu].map(lambda t: tgl(t, pendek=True) + (f", {t:%H}:00" if per_jam else ""))
    for asal, tujuan in [("perkiraan", "Perkiraan"), ("batas_bawah", "Batas bawah"), ("batas_atas", "Batas atas"),
                         ("demand", "Kenyataan")]:
        if asal in d:
            d[tujuan] = d[asal].map(lambda v: ribu(v) if pd.notna(v) else "-")
    return d


def tip(*kolom):
    return [alt.Tooltip(f"{k}:N") for k in kolom]


# ================================================================
# Data
# ================================================================
@st.cache_data
def muat():
    if not (DATA / "perkiraan_seri.parquet").exists():
        return None
    d = {}
    for n in ["seri", "perkiraan_seri", "kota_harian", "kota_per_jam", "riwayat_seri", "riwayat_kota_harian",
              "riwayat_kota_per_jam", "dash_bulanan", "dash_jam", "dash_zona", "dash_tarif"]:
        d[n] = pd.read_parquet(DATA / f"{n}.parquet") if (DATA / f"{n}.parquet").exists() else None
    for n in ["penilaian_uji", "penilaian_uji_per_kelompok", "penilaian_per_jarak",
              "cakupan_rentang_bergulir", "perkiraan_kota_juni_per_pekan"]:
        d[n] = pd.read_csv(DATA / f"{n}.csv") if (DATA / f"{n}.csv").exists() else None
    s = d["seri"]
    s["label"] = s["nama_zona"] + " (" + s["borough"] + ", zona " + s["zona"].astype(str) + ")"
    return d


D = muat()
if D is None:
    st.error("Data aplikasi belum disiapkan. Jalankan `python siapkan_data_app.py` dari folder project, "
             "lalu muat ulang halaman ini.")
    st.stop()

P, SERI = D["perkiraan_seri"], D["seri"]
MULAI, AKHIR = P["jam"].min().normalize(), P["jam"].max().normalize()
ZONA = SERI.drop_duplicates("zona").set_index("zona")
TOTAL_PER_ZONA = P.groupby("zona")["perkiraan"].sum()
DB = D["dash_bulanan"]
BULAN_ADA = sorted(pd.Timestamp(b) for b in DB["bulan"].unique())

# ================================================================
# Judul
# ================================================================
st.markdown(f"""<div class="hero"><h1>Permintaan Ride-Hailing</h1>
<p>Analisis perjalanan Uber dan Lyft {label_bulan(BULAN_ADA)}, dan perkiraan per zona per jam untuk
{MULAI.day} – {tgl(AKHIR, hari=False)}.</p>
<span class="pill">{des(DB['perjalanan'].sum() / 1e6)} juta perjalanan</span>
<span class="pill">{ZONA.shape[0]} zona penjemputan</span>
<span class="pill">Model LightGBM</span>
<span class="pill">Perkiraan hingga 28 hari</span></div>""", unsafe_allow_html=True)

t_dash, t_kota, t_zona, t_rank, t_model, t_tentang = st.tabs(
    ["Dashboard", "Perkiraan kota", "Perkiraan per zona", "Peringkat zona", "Keandalan model", "Tentang"])

NAMA_CARA = {"Rata-rata 4 pekan": "Rata-rata jam yang sama, 4 pekan terakhir",
             "Angka pekan lalu": "Meniru jam yang sama pekan lalu",
             "Rata-rata zona per jam": "Rata-rata jam yang sama, 2024–2025"}
NAMA_UKUR = {"WMAPE": "Meleset per 100 perjalanan", "WMAPE jam sibuk": "Meleset per 100, jam sibuk",
             "Kurang tebak": "Meleset karena terlalu rendah", "Lebih tebak": "Meleset karena terlalu tinggi",
             "Bias %": "Selisih total (%)", "RMSE": "RMSE", "MAE": "MAE"}
NAMA_TINGKAT = {"Seri per jam": "Satu zona-provider per jam", "Kota per jam": "Seluruh kota per jam",
                "Kota per hari": "Seluruh kota per hari", "Zona per hari": "Satu zona per hari"}


def model_ke_depan(m):
    # "7 hari" -> "7 hari ke depan"
    return str(m).replace(" (utama)", "") + " ke depan"


RENTANG_INFO = ("Setiap perkiraan disertai **batas bawah** dan **batas atas**: dalam kondisi normal, "
                "kira-kira 8 dari 10 kali kenyataan berada di antara keduanya.")


# ================================================================
# Tab 1: Dashboard
# ================================================================
with t_dash:
    # ---------- Filter ----------
    pilihan = {f"{label_bulan(BULAN_ADA)} (semua)": BULAN_ADA}
    for th in sorted({b.year for b in BULAN_ADA}):
        bb = [b for b in BULAN_ADA if b.year == th]
        pilihan[label_bulan(bb)] = bb
    with kartu():
        c1, c2, c3 = st.columns([1.4, 1.2, 1])
        periode = c1.selectbox("Periode", list(pilihan))
        prov_d = c2.radio("Provider", ["Uber + Lyft", "Uber", "Lyft"], horizontal=True, key="prov_dash")
        borough_d = c3.selectbox("Borough", ["Semua"] + sorted(b for b in DB["borough"].unique() if b != "Unknown"),
                                 key="bor_dash")
    panduan([
        "<b>Periode</b>: pilih rentang waktu yang ingin dilihat, misalnya satu tahun tertentu.",
        "<b>Provider</b>: lihat Uber saja, Lyft saja, atau keduanya.",
        "<b>Borough</b>: pilih wilayah besar New York, misalnya Manhattan atau Brooklyn, atau biarkan <i>Semua</i>.",
        "<b>Kartu angka</b> di bawahnya ikut berubah. Angka kecil berwarna menunjukkan perubahan dibanding bulan yang sama "
        "setahun sebelumnya: <span style='color:#2E7D4F;font-weight:700'>hijau naik</span>, "
        "<span style='color:#B3261E;font-weight:700'>merah turun</span>.",
        "Arahkan kursor ke grafik untuk melihat angka persisnya."], "Cara menggunakan dashboard")
    BULAN_PILIH = pilihan[periode]
    semua_periode = periode.endswith("(semua)")
    nama_periode = label_bulan(BULAN_PILIH)

    # Pembanding: bulan yang sama setahun sebelumnya.
    # Untuk seluruh periode: Jan–Mei tahun terakhir dibanding Jan–Mei tahun pertama.
    if semua_periode:
        th1, th0 = BULAN_ADA[-1].year, BULAN_ADA[0].year
        bulan_kini = [b for b in BULAN_ADA if b.year == th1]
        bulan_lalu = [b.replace(year=th0) for b in bulan_kini]
    else:
        bulan_kini = BULAN_PILIH
        bulan_lalu = [b - pd.DateOffset(years=1) for b in bulan_kini]
    ada_banding = all(b in BULAN_ADA for b in bulan_lalu)
    teks_banding = (f"{label_bulan(bulan_kini)} dibanding {label_bulan(bulan_lalu)}" if ada_banding
                    else "Tidak ada data tahun sebelumnya untuk dibandingkan")

    def saring(df, bulan=None):
        m = pd.Series(True, index=df.index)
        if bulan is not None:
            m &= df["bulan"].isin(bulan)
        if prov_d != "Uber + Lyft":
            m &= df["provider"] == prov_d
        if borough_d != "Semua" and "borough" in df:
            m &= df["borough"] == borough_d
        return df[m]

    def jumlah_hari(bulan):
        return sum(pd.Timestamp(b).days_in_month for b in bulan)

    per_hari = lambda bulan: saring(DB, bulan)["perjalanan"].sum() / jumlah_hari(bulan)

    tarif = D["dash_tarif"]

    def ukuran(bulan):
        d = saring(tarif, bulan).sum(numeric_only=True)
        return {"Tarif per perjalanan ($)": d["tarif"] / d["perjalanan_tarif"],
                "Jarak per perjalanan (mil)": d["mil"] / d["perjalanan"],
                "Tarif per mil ($)": d["tarif"] / d["mil"],
                "Pendapatan pengemudi per menit ($)": d["pendapatan"] / (d["detik"] / 60),
                "Kecepatan (mph)": d["mil"] / (d["detik"] / 3600)}

    # ---------- Kartu angka utama ----------
    k = st.columns(5)
    with k[0], kpi_kartu(0):
        st.metric("Total perjalanan", singkat(saring(DB, BULAN_PILIH)['perjalanan'].sum()))
        st.caption(f"{nama_periode} · rata-rata **{ribu(per_hari(BULAN_PILIH))}** per hari")
    with k[1], kpi_kartu(1):
        if ada_banding:
            st.metric("Pertumbuhan rata-rata perjalanan per hari (%)", persen((per_hari(bulan_kini) / per_hari(bulan_lalu) - 1) * 100).replace("%", ""))
        else:
            st.metric("Pertumbuhan rata-rata perjalanan per hari (%)", "-")
        st.caption(teks_banding)
    if tarif is not None:
        u = ukuran(BULAN_PILIH)
        u_kini, u_lalu = ukuran(bulan_kini), (ukuran(bulan_lalu) if ada_banding else None)
        delta = {n: (u_kini[n] / u_lalu[n] - 1) * 100 for n in u} if ada_banding else {}
        for kol, (nama, satuan, kunci) in zip(k[2:], [("Tarif per mil ($)", "$", "Tarif per mil ($)"),
                                                      ("Pendapatan pengemudi per menit ($)", "$", "Pendapatan pengemudi per menit ($)"),
                                                      ("Kecepatan rata-rata (mph)", "mph", "Kecepatan (mph)")]):
            nilai = des(u[kunci], 2) if satuan == "$" else des(u[kunci], 1)
            with kol, kpi_kartu(k.index(kol)):
                st.metric(nama, nilai, ubah(delta[kunci]) if ada_banding else None)
                st.caption(f"{nama_periode} · perubahan {teks_banding}" if ada_banding else f"{nama_periode} · {teks_banding}")
    else:
        for kol, (lbl, v) in zip(k[2:], [("Tarif per mil", "+11,5%"), ("Pendapatan pengemudi per menit", "+7,6%"),
                                         ("Kecepatan rata-rata perjalanan", "−3,3%")]):
            with kol, kpi_kartu(k.index(kol)):
                st.metric(lbl, v)
                st.caption("Hasil Business Analytics, Jan–Mei 2026 dibanding Jan–Mei 2024")

    # ---------- Perjalanan per bulan ----------
    with kartu():
        st.subheader(f"Jumlah perjalanan per bulan, {nama_periode}")
        st.caption("Uber dan Lyft ditumpuk; tinggi keseluruhan = seluruh perjalanan dalam bulan itu")
        bl = saring(DB, BULAN_PILIH).groupby(["bulan", "provider"], as_index=False)["perjalanan"].sum()
        bl["Bulan"] = bl["bulan"].map(lambda b: f"{BULAN_PANJANG[b.month - 1]} {b.year}")
        bl["Perjalanan"] = bl["perjalanan"].map(ribu)
        bl["Provider"] = bl["provider"]
        area = alt.Chart(bl).mark_area().encode(
            x=alt.X("bulan:T", title=None, axis=sumbu_bulan(len(BULAN_PILIH))),
            y=alt.Y("perjalanan:Q", stack="zero", axis=sumbu_angka("Perjalanan per bulan")),
            color=alt.Color("provider:N", title="Provider", scale=alt.Scale(domain=["Uber", "Lyft"], range=[W["utama"], W["lyft"]])),
            order=alt.Order("provider:N", sort="descending"),
            tooltip=tip("Bulan", "Provider", "Perjalanan"))
        st.altair_chart(area.properties(height=320), width="stretch")
        tb = saring(DB).groupby("bulan")["perjalanan"].sum()
        tb = tb / tb.index.map(lambda b: pd.Timestamp(b).days_in_month)
        yoy = (tb / tb.shift(12) - 1).dropna() * 100
        a, b = yoy[(yoy.index >= "2025-01-01") & (yoy.index < "2025-10-01")], yoy[yoy.index >= "2025-10-01"]
        if len(a) and len(b):
            st.caption(f"Seluruh periode: pada Januari–September 2025, rata-rata perjalanan per hari **{persen(a.mean())}** "
                       f"dibanding bulan yang sama tahun sebelumnya; sejak Oktober 2025 menjadi **{persen(b.mean())}**. "
                       "Artinya pertumbuhan mulai lebih cepat sejak Oktober 2025.")

    kiri, kanan = st.columns(2)
    # ---------- Peta panas jam × hari ----------
    with kiri, kartu():
        st.subheader("Kapan paling ramai")
        st.caption(f"Rata-rata perjalanan per jam menurut hari dan jam · makin gelap makin ramai · {nama_periode}")
        dj = saring(D["dash_jam"], BULAN_PILIH).groupby(["hari", "jam_hari"], as_index=False)["perjalanan"].sum()
        tanggal = pd.date_range(BULAN_PILIH[0], BULAN_PILIH[-1] + pd.offsets.MonthEnd(0))
        n_hari = pd.Series(tanggal.dayofweek + 1).value_counts()
        dj["rata"] = dj["perjalanan"] / dj["hari"].map(n_hari)
        dj["Hari"] = dj["hari"].map(lambda h: HARI[h - 1])
        dj["Jam"] = dj["jam_hari"].map(lambda h: f"{h:02d}:00")
        dj["Rata-rata perjalanan per jam"] = dj["rata"].map(ribu)
        peta = alt.Chart(dj).mark_rect().encode(
            x=alt.X("jam_hari:O", title="Jam"), y=alt.Y("Hari:N", title=None, sort=HARI),
            color=alt.Color("rata:Q", title="Perjalanan per jam", scale=alt.Scale(range=["#EEF3F3", W["utama"]]),
                            legend=alt.Legend(labelExpr=ANGKA_EXPR)),
            tooltip=tip("Hari", "Jam", "Rata-rata perjalanan per jam"))
        st.altair_chart(peta.properties(height=280), width="stretch")
        if len(dj):
            per_jam = dj.groupby("jam_hari")["rata"].mean()
            per_hr = dj.groupby("Hari")["rata"].mean()
            st.caption(f"Jam teramai **{per_jam.idxmax():02d}:00**, **{des(per_jam.max() / per_jam.min())} kali** jam tersepi "
                       f"({per_jam.idxmin():02d}:00). Hari teramai **{per_hr.idxmax()}**, tersepi {per_hr.idxmin()}.")

    # ---------- Zona teramai ----------
    with kanan, kartu():
        st.subheader("10 zona penjemputan teramai")
        st.caption(f"Persen dari seluruh perjalanan · {nama_periode}")
        dz = D["dash_zona"].copy()
        dz["borough"] = dz["zona"].map(ZONA["borough"]).fillna("Unknown")
        dz = saring(dz, BULAN_PILIH).groupby("zona", as_index=False)["perjalanan"].sum()
        dz["porsi"] = dz["perjalanan"] / dz["perjalanan"].sum() * 100
        z10 = dz.nlargest(10, "perjalanan").copy()
        z10["Zona"] = z10["zona"].map(ZONA["nama_zona"]).fillna("Zona") + " (" + z10["zona"].astype(str) + ")"
        z10["Perjalanan"] = z10["perjalanan"].map(ribu)
        z10["Porsi"] = z10["porsi"].map(lambda v: des(v, 2) + "%")
        bar = alt.Chart(z10).mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("porsi:Q", scale=alt.Scale(range=["#8CCBC2", "#1F5F6B"]), legend=None),
            x=alt.X("porsi:Q", axis=alt.Axis(title="Persen dari seluruh perjalanan",
                                             labelExpr="replace(format(datum.value, '.1f'), '.', ',')")),
            y=alt.Y("Zona:N", sort="-x", title=None), tooltip=tip("Zona", "Perjalanan", "Porsi"))
        st.altair_chart(bar.properties(height=280), width="stretch")
        urut = dz.sort_values("perjalanan", ascending=False)["porsi"].cumsum()
        st.caption(f"10 zona teratas menampung **{des(z10['porsi'].sum())}%** perjalanan; "
                   f"butuh **{int((urut < 50).sum()) + 1} zona** untuk mencapai separuhnya.")

    kiri, kanan = st.columns(2)
    # ---------- Tabel tarif ----------
    with kiri, kartu():
        st.subheader("Tarif dan pendapatan pengemudi")
        if tarif is not None and ada_banding:
            st.caption(f"{teks_banding} · bulan yang sama dibandingkan agar tidak tercampur musim · hijau naik, merah turun")
            u0, u1 = ukuran(bulan_lalu), ukuran(bulan_kini)
            tt = pd.DataFrame({"Ukuran": list(u0), label_bulan(bulan_lalu): list(u0.values()),
                               label_bulan(bulan_kini): list(u1.values()),
                               "Perubahan": [(u1[n] / u0[n] - 1) * 100 for n in u0]})
            gaya = (tt.style.format({label_bulan(bulan_lalu): lambda v: des(v, 2), label_bulan(bulan_kini): lambda v: des(v, 2),
                                     "Perubahan": persen})
                    .map(lambda v: f"color: {W['naik'] if v > 0 else W['turun']}; font-weight: 700", subset=["Perubahan"]))
            st.dataframe(gaya, hide_index=True, width="stretch")
            st.caption("Tarif dalam dolar AS, sebelum pajak dan biaya tambahan. Pendapatan pengemudi per menit perjalanan.")
        elif tarif is not None:
            st.caption(f"{nama_periode} · tidak ada data tahun sebelumnya untuk dibandingkan")
            tt = pd.DataFrame({"Ukuran": list(u), nama_periode: list(u.values())})
            st.dataframe(tabel(tt, desimal={nama_periode: 2}), hide_index=True, width="stretch")
        else:
            st.info("Tabel tarif belum tersedia: kolom file `business_pickup_2024_2026.parquet` tidak dikenali oleh "
                    "`siapkan_data_app.py`.")

    # ---------- Temuan utama ----------
    with kanan, kartu():
        st.subheader("Temuan utama dari analisis bisnis")
        st.markdown("""
- **Permintaan tersebar, tidak terpusat.** 10 zona teratas hanya 12,9% perjalanan; butuh 58 zona untuk mencapai separuhnya.
- **Tidak ada satu jam puncak untuk seluruh kota.** Zona terbagi tiga: memuncak pagi, sore, atau malam.
- **Akhir pekan adalah Jumat–Sabtu,** bukan Sabtu–Minggu. Sabtu 36% lebih ramai dari Senin.
- **Tarif naik lebih cepat dari yang terlihat.** Per mil +11,5%, karena perjalanan juga makin pendek.
- **Pangsa Uber menurun** di 243 dari 261 zona, walau masih 72–76% di separuh zona.
""")
        st.caption("Seluruh periode Januari 2024 – Mei 2026, tidak mengikuti filter.")


# ================================================================
# Tab 2: Perkiraan kota
# ================================================================
with t_kota:
    panduan([
        "<b>Empat kartu di atas</b> adalah perkiraan jumlah perjalanan di seluruh kota untuk setiap pekan Juni, beserta "
        "kisarannya.",
        "<b>Grafik</b> menyambung data nyata 4 pekan terakhir (garis gelap) dengan perkiraan 4 pekan ke depan (garis "
        "berwarna). Area berwarna di sekitarnya adalah kisaran normal. Arahkan kursor ke titik untuk melihat angkanya.",
        "<b>Tabel</b> di bawahnya merinci angka per pekan dan per hari.",
        "Untuk melihat satu zona tertentu, buka tab <i>Perkiraan per zona</i>."], "Cara membaca halaman ini")
    st.markdown(RENTANG_INFO)
    kh = D["kota_harian"].copy()
    kh["pekan"] = ((kh["tanggal"] - MULAI).dt.days // 7).astype(int)
    for kol_, (_, g) in zip(st.columns(kh["pekan"].nunique()), kh.groupby("pekan")):
        with kol_, kpi_kartu(int(g["pekan"].iloc[0])):
            akhir_p = g["tanggal"].max()
            st.metric(f"Perkiraan perjalanan, {g['tanggal'].min().day}–{akhir_p.day} {BULAN_PANJANG[akhir_p.month - 1]}",
                      singkat(g['perkiraan'].sum(), 2))
            st.caption(f"Rentang **{rentang_singkat(g['batas_bawah'].sum(), g['batas_atas'].sum())}** perjalanan · "
                       f"model {model_ke_depan(g['model'].iloc[0])}")

    with kartu():
        st.subheader("Jumlah perjalanan per hari di seluruh kota: 4 pekan terakhir dan perkiraan 4 pekan ke depan")
        rk = D["riwayat_kota_harian"]
        rk = siapkan_tooltip(rk[rk["tanggal"] >= MULAI - pd.Timedelta(days=28)], "tanggal")
        st.caption(f"{rk['tanggal'].min().day} {BULAN[rk['tanggal'].min().month - 1]} – {rk['tanggal'].max().day} "
                   f"{BULAN[rk['tanggal'].max().month - 1]} adalah data nyata; {MULAI.day}–{AKHIR.day} "
                   f"{BULAN[AKHIR.month - 1]} adalah perkiraan beserta rentang batas bawah – batas atas")
        khx = siapkan_tooltip(kh, "tanggal")
        khx["Model"] = khx["model"].map(model_ke_depan)
        tip_kota = tip("Waktu", "Perkiraan", "Batas bawah", "Batas atas", "Model")
        sb = sumbu_tanggal(56)
        area = alt.Chart(khx).mark_area(opacity=0.22).encode(
            x=alt.X("tanggal:T", title=None, axis=sb), y=alt.Y("batas_bawah:Q", axis=sumbu_angka("Perjalanan per hari")),
            y2="batas_atas:Q", color=alt.Color("model:N", scale=MODEL_WARNA, legend=None), tooltip=tip_kota)
        garis = alt.Chart(khx).mark_line(point=True, strokeWidth=2.5).encode(
            x="tanggal:T", y="perkiraan:Q", color=alt.Color("model:N", title="Perkiraan, model … ke depan", scale=MODEL_WARNA),
            strokeDash=alt.StrokeDash("model:N", scale=MODEL_GARIS, legend=None), tooltip=tip_kota)
        nyata = alt.Chart(rk).mark_line(point=True, color=W["nyata"], strokeWidth=1.8).encode(
            x="tanggal:T", y="demand:Q", tooltip=tip("Waktu", "Kenyataan"))
        st.altair_chart((area + nyata + garis).properties(height=380), width="stretch")
        st.caption("Garis gelap: data nyata. Garis berwarna: perkiraan; model 28 hari digambar putus-putus. Makin jauh "
                   "tanggalnya, makin jauh ke depan perkiraan itu dibuat, dan makin lebar rentangnya.")

    kiri, kanan = st.columns(2)
    if D["perkiraan_kota_juni_per_pekan"] is not None:
        with kiri, kartu():
            st.subheader(f"Perkiraan total perjalanan seluruh kota per pekan, {BULAN_PANJANG[MULAI.month - 1]} {MULAI.year}")
            st.caption("Jumlah perjalanan Uber dan Lyft di semua zona dalam setiap pekan, beserta model yang dipakai")
            t = D["perkiraan_kota_juni_per_pekan"].copy()
            t["Model"] = t["Model"].str.replace("jarak ", "", regex=False).map(model_ke_depan)
            t = t.rename(columns={"Lebar rentang": "Lebar rentang (% dari perkiraan)"})
            st.dataframe(tabel(t, ribuan=["Batas bawah", "Perkiraan", "Batas atas"], persen_kol={"Lebar rentang (% dari perkiraan)": 0}),
                         hide_index=True, width="stretch")
    pekan1 = kh[kh["pekan"] == 0]
    with kanan, kartu():
        st.subheader(f"Perkiraan total perjalanan seluruh kota per hari, {pekan1['tanggal'].min().day}–"
                     f"{tgl(pekan1['tanggal'].max(), hari=False)}")
        st.caption("Rincian harian pekan pertama, memakai model 7 hari ke depan, yang paling akurat")
        h1 = pd.DataFrame({"Hari": pekan1["tanggal"].dt.dayofweek.map(dict(enumerate(HARI))),
                           "Tanggal": pekan1["tanggal"].map(lambda t: tgl(t, hari=False, pendek=True)),
                           "Batas bawah": pekan1["batas_bawah"], "Perkiraan": pekan1["perkiraan"], "Batas atas": pekan1["batas_atas"]})
        st.dataframe(tabel(h1, ribuan=["Batas bawah", "Perkiraan", "Batas atas"]), hide_index=True, width="stretch")
        if len(pekan1) == 7:
            s = pekan1.set_index(pekan1["tanggal"].dt.dayofweek)["perkiraan"]
            st.caption(f"Sabtu diperkirakan **{des((s[5] / s[0] - 1) * 100, 0)}% lebih ramai** dari Senin.")

    with st.expander(f"Lihat perkiraan per jam seluruh kota, {pekan1['tanggal'].min().day}–{tgl(pekan1['tanggal'].max(), hari=False)}"):
        kj = siapkan_tooltip(D["kota_per_jam"], "jam", per_jam=True)
        rj = siapkan_tooltip(D["riwayat_kota_per_jam"], "jam", per_jam=True)
        sb = sumbu_tanggal(21)
        tip_j = tip("Waktu", "Perkiraan", "Batas bawah", "Batas atas")
        a = alt.Chart(kj).mark_area(opacity=0.25, color=W["rentang"]).encode(
            x=alt.X("jam:T", title=None, axis=sb), y=alt.Y("batas_bawah:Q", axis=sumbu_angka("Perjalanan per jam")),
            y2="batas_atas:Q", tooltip=tip_j)
        g1 = alt.Chart(kj).mark_line(color=W["utama"], strokeWidth=2).encode(x="jam:T", y="perkiraan:Q", tooltip=tip_j)
        g2 = alt.Chart(rj).mark_line(color=W["nyata"], strokeWidth=1.2).encode(x="jam:T", y="demand:Q", tooltip=tip("Waktu", "Kenyataan"))
        st.altair_chart((a + g2 + g1).properties(height=320), width="stretch")
        st.caption("Data nyata 2 pekan terakhir (gelap), lalu perkiraan per jam pekan pertama dengan rentangnya.")


# ================================================================
# Tab 3: Perkiraan per zona
# ================================================================
with t_zona:
    st.markdown(RENTANG_INFO)
    with kartu():
        c1, c2, c3 = st.columns([1, 2, 1.2])
        borough = c1.selectbox("Borough", ["Semua"] + sorted(ZONA["borough"].unique()))
        pil = ZONA if borough == "Semua" else ZONA[ZONA["borough"] == borough]
        urut = pil.assign(t=TOTAL_PER_ZONA.reindex(pil.index).fillna(0)).sort_values("t", ascending=False)
        zona = c2.selectbox("Zona (urut dari perkiraan terbesar)", urut.index, format_func=lambda z: urut.loc[z, "label"])
        provider_ada = sorted(SERI.loc[SERI["zona"] == zona, "provider"].unique())
        provider = c3.radio("Provider", provider_ada + (["Uber + Lyft"] if len(provider_ada) > 1 else []), horizontal=True)
        rentang_tgl = st.slider("Tanggal", min_value=MULAI.date(), max_value=AKHIR.date(),
                                value=(MULAI.date(), min(MULAI + pd.Timedelta(days=6), AKHIR).date()), format="DD MMM YYYY")
    panduan([
        "<b>Pilih borough</b>, yaitu wilayah besar New York seperti Manhattan, Brooklyn, atau Queens. Biarkan <i>Semua</i> "
        "untuk melihat semua zona.",
        "<b>Pilih zona</b>. Daftarnya diurutkan dari perkiraan perjalanan terbanyak. Klik kotaknya lalu ketik nama untuk "
        "mencari, misalnya <i>Airport</i> atau <i>Midtown</i>.",
        "<b>Pilih provider</b>: Uber, Lyft, atau Uber + Lyft untuk gabungan keduanya.",
        "<b>Geser dua titik</b> pada garis <i>Tanggal</i> untuk memilih hari yang ingin dilihat, antara 1 dan 28 Juni. "
        "Perkiraan 1–7 Juni paling akurat; makin jauh tanggalnya, makin lebar kisarannya.",
        "<b>Baca grafik</b>: garis gelap adalah jumlah perjalanan yang benar-benar terjadi 2 pekan terakhir, garis teal "
        "adalah perkiraan, dan area teal muda adalah kisaran normal. Dalam kondisi biasa, 8 dari 10 kali jumlah "
        "sebenarnya berada di dalam area itu. Arahkan kursor ke grafik untuk melihat angkanya per jam.",
        "<b>Simpan hasilnya</b> dengan tombol <i>Unduh perkiraan per jam (CSV)</i> di bagian paling bawah; file itu bisa "
        "dibuka di Excel atau Google Sheets."])
    dari, sampai = pd.Timestamp(rentang_tgl[0]), pd.Timestamp(rentang_tgl[1]) + pd.Timedelta(days=1)
    akhir_z = sampai - pd.Timedelta(days=1)
    label_periode = f"{dari.day} {BULAN[dari.month - 1]} – {akhir_z.day} {BULAN[akhir_z.month - 1]}"

    prov = provider_ada if provider == "Uber + Lyft" else [provider]
    f = P[(P["zona"] == zona) & P["provider"].isin(prov) & (P["jam"] >= dari) & (P["jam"] < sampai)]
    r = D["riwayat_seri"]
    r = r[(r["zona"] == zona) & r["provider"].isin(prov) & (r["jam"] >= MULAI - pd.Timedelta(days=14))]
    r = r.groupby("jam", as_index=False)["demand"].sum()
    satu = len(prov) == 1
    if satu:
        f = f[["jam", "batas_bawah", "perkiraan", "batas_atas", "jarak", "cara"]]
    else:
        f = f.groupby("jam", as_index=False).agg(perkiraan=("perkiraan", "sum"), jarak=("jarak", "first"), cara=("cara", "first"))
    info = SERI[(SERI["zona"] == zona) & SERI["provider"].isin(prov)].iloc[0]
    nama = f"{ZONA.loc[zona, 'nama_zona']}, {provider}"

    # Kartu mengikuti KPI utama project: jumlah perjalanan per zona per jam per provider
    m = st.columns(4)
    n_jam = max(len(f), 1)
    rata_jam = f["perkiraan"].sum() / n_jam
    rata_nyata = r["demand"].mean() if len(r) else np.nan
    with m[0], kpi_kartu(0):
        st.metric("Rata-rata perkiraan perjalanan per jam", ribu(rata_jam),
                  ubah((rata_jam / rata_nyata - 1) * 100) if pd.notna(rata_nyata) and rata_nyata > 0 else None)
        st.caption(f"KPI utama · dibanding rata-rata nyata 2 pekan terakhir (**{ribu(rata_nyata)}** per jam)"
                   if pd.notna(rata_nyata) else "KPI utama · belum ada data nyata 2 pekan terakhir")
    if len(f):
        pk = f.loc[f["perkiraan"].idxmax()]
        with m[1], kpi_kartu(1):
            st.metric("Perkiraan tertinggi dalam satu jam", ribu(pk["perkiraan"]))
            teks = f"**{HARI[pk['jam'].dayofweek]} {pk['jam'].day} {BULAN[pk['jam'].month - 1]}, {pk['jam']:%H}:00**"
            if satu:
                teks += f" · kisaran {ribu(pk['batas_bawah'])}–{ribu(pk['batas_atas'])}"
            st.caption(teks)
        with m[2], kpi_kartu(2):
            profil = f.groupby(f["jam"].dt.hour)["perkiraan"].mean()
            jp = int(profil.idxmax())
            waktu = "pagi" if 6 <= jp <= 11 else "siang" if 12 <= jp <= 16 else "sore" if 17 <= jp <= 19 else "malam"
            st.metric(f"Jam paling ramai dalam sehari, {waktu} hari", f"{jp:02d}:00")
            st.caption(f"Rata-rata **{ribu(profil.max())}** perjalanan pada jam itu")
    with m[3], kpi_kartu(3):
        st.metric("Total perkiraan perjalanan", ribu(f["perkiraan"].sum()))
        st.caption(f"{label_periode} · {f['jam'].dt.normalize().nunique()} hari")

    with kartu():
        st.subheader(f"Perkiraan perjalanan per jam: {nama}")
        st.caption(f"2 pekan data nyata terakhir, lalu perkiraan {label_periode}"
                   + (" beserta rentang batas bawah – batas atas" if satu else ""))
        fx, rx = siapkan_tooltip(f, "jam", per_jam=True), siapkan_tooltip(r, "jam", per_jam=True)
        fx["Model"] = fx["jarak"].map(lambda j: f"{j} hari ke depan")
        sb = sumbu_tanggal(14 + (sampai - dari).days)
        tip_z = tip("Waktu", "Perkiraan", *(["Batas bawah", "Batas atas"] if satu else []), "Model")
        lapisan = []
        if satu:
            lapisan.append(alt.Chart(fx).mark_area(opacity=0.22, color=W["rentang"]).encode(
                x=alt.X("jam:T", title=None, axis=sb), y=alt.Y("batas_bawah:Q", axis=sumbu_angka("Perjalanan per jam")),
                y2="batas_atas:Q", tooltip=tip_z))
        lapisan.append(alt.Chart(rx).mark_line(color=W["nyata"], strokeWidth=1.2).encode(
            x=alt.X("jam:T", title=None, axis=sb), y=alt.Y("demand:Q", axis=sumbu_angka("Perjalanan per jam")),
            tooltip=tip("Waktu", "Kenyataan")))
        lapisan.append(alt.Chart(fx).mark_line(color=W["utama"], strokeWidth=2).encode(x="jam:T", y="perkiraan:Q", tooltip=tip_z))
        st.altair_chart(alt.layer(*lapisan).properties(height=380), width="stretch")
        catatan = ["Garis gelap: data nyata. Garis teal: perkiraan."]
        catatan.append("Area teal muda: rentang batas bawah – batas atas." if satu else
                       "Rentang tidak ditampilkan untuk Uber + Lyft: menjumlahkan batas kedua provider menghasilkan "
                       "rentang yang terlalu lebar. Pilih satu provider untuk melihat rentangnya.")
        if (f["cara"] == "Rata-rata 4 pekan").any():
            catatan.append("Zona dan provider ini termasuk 5% permintaan paling sepi yang tidak dimodelkan; perkiraannya "
                           "memakai rata-rata jam yang sama 4 pekan terakhir.")
        st.caption(" ".join(catatan))

    with kartu():
        st.subheader(f"Perkiraan perjalanan per hari: {nama}, {label_periode}")
        st.caption("Total perkiraan setiap hari, dan jam dengan perkiraan tertinggi pada hari itu")
        h = f.assign(tanggal=f["jam"].dt.normalize())
        rh = h.groupby("tanggal").agg(perkiraan=("perkiraan", "sum"), idx=("perkiraan", "idxmax"),
                                      tertinggi=("perkiraan", "max"), jarak=("jarak", "first")).reset_index()
        tabel_h = pd.DataFrame({"Hari": rh["tanggal"].dt.dayofweek.map(dict(enumerate(HARI))),
                                "Tanggal": rh["tanggal"].map(lambda t: tgl(t, hari=False, pendek=True)),
                                "Perkiraan per hari": rh["perkiraan"],
                                "Jam dengan perkiraan tertinggi": h.loc[rh["idx"], "jam"].dt.strftime("%H:00").values,
                                "Perkiraan di jam itu": rh["tertinggi"],
                                "Model": rh["jarak"].map(lambda j: f"{j} hari ke depan")})
        st.dataframe(tabel(tabel_h, ribuan=["Perkiraan per hari", "Perkiraan di jam itu"]), hide_index=True, width="stretch")
        unduh = f.drop(columns=["cara"]).copy()
        for kk in ["batas_bawah", "perkiraan", "batas_atas"]:
            if kk in unduh:
                unduh[kk] = unduh[kk].round().astype("int64")
        st.download_button("Unduh perkiraan per jam (CSV)", unduh.to_csv(index=False).encode("utf-8"),
                           file_name=f"perkiraan_zona{zona}_{provider.replace(' + ', '_')}_{rentang_tgl[0]:%Y%m%d}_{rentang_tgl[1]:%Y%m%d}.csv",
                           mime="text/csv", type="primary", icon=":material/download:")


# ================================================================
# Tab 4: Peringkat zona
# ================================================================
with t_rank:
    with kartu():
        c1, c2, c3, c4 = st.columns([1.1, 1.5, 1.2, 0.8])
        hari_pilih = c1.date_input("Tanggal", value=MULAI.date(), min_value=MULAI.date(), max_value=AKHIR.date(), format="DD/MM/YYYY")
        jam_pilih = c2.slider("Jam", 0, 23, (17, 21), help="Termasuk jam awal dan jam akhir")
        prov_r = c3.radio("Provider", ["Uber + Lyft"] + sorted(SERI["provider"].unique()), horizontal=True, key="prov_rank")
        n_atas = c4.selectbox("Jumlah zona", [10, 15, 20, 30])

    panduan([
        "<b>Pilih tanggal</b> antara 1 dan 28 Juni.",
        "<b>Geser dua titik</b> pada garis <i>Jam</i> untuk memilih jam awal dan akhir, misalnya 07–09 untuk jam berangkat "
        "kerja atau 17–21 untuk jam pulang.",
        "<b>Pilih provider</b>: Uber + Lyft, Uber, atau Lyft.",
        "<b>Pilih jumlah zona</b> yang ingin ditampilkan.",
        "<b>Baca hasilnya</b>: makin panjang batang, makin banyak perjalanan yang diperkirakan di zona itu. "
        "<i>Bagian dari total kota</i> menunjukkan berapa persen seluruh perjalanan di kota pada jam itu yang terjadi di "
        "zona tersebut. Zona teratas "
        "adalah tempat pengemudi paling dibutuhkan."])
    t0 = pd.Timestamp(hari_pilih)
    q = P[(P["jam"].dt.normalize() == t0) & P["jam"].dt.hour.between(*jam_pilih)]
    if prov_r != "Uber + Lyft":
        q = q[q["provider"] == prov_r]
    rank = q.groupby("zona")["perkiraan"].sum().sort_values(ascending=False).head(n_atas).reset_index()
    rank["Zona"] = rank["zona"].map(ZONA["nama_zona"]) + " (" + rank["zona"].astype(str) + ")"
    rank["Borough"] = rank["zona"].map(ZONA["borough"])
    total_kota = q["perkiraan"].sum()
    rank["porsi"] = rank["perkiraan"] / total_kota * 100 if total_kota else 0
    rank["Perkiraan"] = rank["perkiraan"].map(ribu)
    rank["Bagian dari total kota"] = rank["porsi"].map(lambda v: des(v) + "%")
    jam_label = f"{jam_pilih[0]:02d}:00–{jam_pilih[1]:02d}:59"

    with kartu():
        st.subheader(f"Zona dengan perkiraan perjalanan terbanyak: {tgl(t0)}, {jam_label}")
        st.caption(f"{prov_r} · total seluruh kota **{ribu(total_kota)} perjalanan**; {n_atas} zona teratas menampung "
                   f"**{des(rank['porsi'].sum())}%**")
        bar = alt.Chart(rank).mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("perkiraan:Q", scale=alt.Scale(range=["#8CCBC2", "#1F5F6B"]), legend=None),
            x=alt.X("perkiraan:Q", axis=sumbu_angka("Perkiraan perjalanan")), y=alt.Y("Zona:N", sort="-x", title=None),
            tooltip=tip("Zona", "Borough", "Perkiraan", "Bagian dari total kota"))
        st.altair_chart(bar.properties(height=max(260, 26 * len(rank))), width="stretch")

    with kartu():
        st.subheader(f"Rincian {n_atas} zona dengan perkiraan perjalanan terbanyak")
        st.caption("Bagian dari total kota: persen perkiraan perjalanan seluruh kota pada tanggal dan jam yang dipilih "
                   "yang terjadi di zona itu")
        tr = rank[["Zona", "Borough", "perkiraan", "porsi"]].rename(columns={"perkiraan": "Perkiraan perjalanan",
                                                                            "porsi": "Bagian dari total kota"})
        st.dataframe(tabel(tr, ribuan=["Perkiraan perjalanan"], persen_kol={"Bagian dari total kota": 1}), hide_index=True, width="stretch")


# ================================================================
# Tab 5: Keandalan model
# ================================================================
def bacaan(dilihat, hasil, kenapa):
    st.markdown(f"**Yang dilihat.** {dilihat}\n\n**Hasilnya.** {hasil}\n\n**Kenapa.** {kenapa}")


with t_model:
    st.markdown(f"Model: **LightGBM**, **satu model untuk seluruh {int(SERI['dimodelkan'].sum())} kombinasi zona dan provider** "
                "(misalnya LaGuardia–Uber atau LaGuardia–Lyft; selanjutnya disebut **seri**) yang menampung **95% permintaan**. Dinilai pada **Januari–Mei 2026**, periode yang **tidak dipakai untuk melatih atau "
                "memilih model**, dan dibandingkan dengan **cara sederhana yang biasa dipakai tanpa model**.")
    u = D["penilaian_uji"]
    if u is not None:
        u = u.rename(columns={u.columns[0]: "Cara"})
        u = pd.concat([u.iloc[[0]].assign(Cara="Model LightGBM"),
                       u[u["Cara"].isin(["Rata-rata 4 pekan", "Angka pekan lalu", "Rata-rata zona per jam"])]], ignore_index=True)
        mo, pb4, pbl = u.iloc[0], u.loc[u["Cara"] == "Rata-rata 4 pekan"].iloc[0], u.loc[u["Cara"] == "Angka pekan lalu"].iloc[0]
        lebih4 = (1 - mo["WMAPE"] / pb4["WMAPE"]) * 100     # kesalahan model berapa persen lebih sedikit
        lebihl = (1 - mo["WMAPE"] / pbl["WMAPE"]) * 100
        tepat = 100 - mo["WMAPE"]
        k = st.columns(4)
        for kol, (lbl, v, ket) in zip(k, [("Model LightGBM: meleset per 100 perjalanan", des(mo["WMAPE"]), f"Tepat sekitar **{des(tepat, 0)}%**; makin kecil makin baik"),
                                          ("Tanpa model, rata-rata 4 pekan: meleset per 100", des(pb4["WMAPE"]), f"Kesalahan model **{des(lebih4, 0)}% lebih sedikit**"),
                                          ("Tanpa model, meniru pekan lalu: meleset per 100", des(pbl["WMAPE"]), f"Kesalahan model **{des(lebihl, 0)}% lebih sedikit**"),
                                          ("Model di jam sibuk 17:00–22:00: meleset per 100", des(mo["WMAPE jam sibuk"]),
                                           f"Tanpa model (rata-rata 4 pekan): **{des(pb4['WMAPE jam sibuk'])}**")]):
            with kol, kpi_kartu(k.index(kol)):
                st.metric(lbl, v)
                st.caption(ket)

        with kartu():
            st.subheader("Akurasi model dibanding cara perkiraan tanpa model, Januari–Mei 2026")
            st.caption("Angka = berapa perjalanan yang meleset dari setiap 100 · makin kecil makin baik")
            ut = u.copy()
            ut["Cara"] = ut["Cara"].map(lambda c: NAMA_CARA.get(c, c))
            ut = ut.rename(columns=NAMA_UKUR)
            st.dataframe(tabel(ut, desimal={c: 2 for c in ut.columns[1:] if c != "Selisih total (%)"},
                               persen_kol={"Selisih total (%)": 1}), hide_index=True, width="stretch")
            st.caption("**Meleset karena terlalu rendah + meleset karena terlalu tinggi = meleset per 100 perjalanan.** "
                       "**Selisih total** membandingkan jumlah seluruh perkiraan dengan jumlah seluruh kenyataan; negatif berarti "
                       "perkiraan secara keseluruhan terlalu rendah. **RMSE** dan **MAE** adalah rata-rata selisih dalam jumlah "
                       "perjalanan per jam per zona-provider; RMSE memberi hukuman lebih berat pada selisih yang besar.")
            arah = "di bawah" if mo["Bias %"] < 0 else "di atas"
            bacaan(
                "**Seberapa sering setiap cara salah** saat menebak jumlah perjalanan per zona per jam pada Januari–Mei 2026. "
                "**Baris pertama adalah model**; tiga baris lainnya adalah cara yang bisa dipakai tanpa model. Kolom utama "
                "adalah **meleset per 100 perjalanan**: dari setiap 100 perjalanan yang benar-benar terjadi, berapa yang "
                "tidak tertebak.",
                f"Model meleset **{des(mo['WMAPE'])} dari setiap 100 perjalanan**, atau **tepat sekitar {des(tepat, 0)}%**. "
                f"Cara terbaik tanpa model, rata-rata jam yang sama 4 pekan terakhir, meleset {des(pb4['WMAPE'])}. Artinya "
                f"**kesalahan model {des(lebih4, 0)}% lebih sedikit**, dan {des(lebihl, 0)}% lebih sedikit dibanding meniru "
                f"jam yang sama pekan lalu. Model juga **lebih sedikit meleset di jam sibuk** ({des(mo['WMAPE jam sibuk'])} "
                f"dibanding {des(pb4['WMAPE jam sibuk'])} per 100) dan punya **RMSE paling kecil**, sehingga **lebih jarang "
                f"meleset jauh**. Dari {des(mo['WMAPE'])} perjalanan yang meleset, {des(mo['Kurang tebak'])} karena perkiraan "
                f"**terlalu rendah** dan {des(mo['Lebih tebak'])} karena terlalu tinggi; jika seluruh perkiraan dijumlahkan, "
                f"hasilnya {des(abs(mo['Bias %']))}% {arah} jumlah kenyataan.",
                "Cara tanpa model hanya memakai **satu sumber informasi**, misalnya jumlah perjalanan pekan lalu saja. Model "
                "**menggabungkan banyak sumber**: jumlah perjalanan 1 sampai 4 pekan sebelumnya, rata-rata dan nilai tengahnya, "
                "tingkat permintaan terbaru, hari, jam, hari libur, dan jam ramai tiap zona. **Nilai tengah (median) 4 pekan** "
                "membuat satu hari yang anjlok tidak langsung menarik perkiraan pekan berikutnya, sehingga meleset jauh lebih "
                "jarang. Perkiraan yang cenderung terlalu rendah kemungkinan karena **permintaan sedang tumbuh**: model belajar "
                "dari pekan-pekan sebelumnya, yang jumlahnya sedikit lebih rendah dari sekarang. Karena itu, di jam dan zona yang "
                "mahal bila kekurangan pengemudi, **batas atas lebih aman dipakai sebagai acuan**.")

    kiri, kanan = st.columns(2)
    if D["penilaian_uji_per_kelompok"] is not None:
        with kiri, kartu():
            st.subheader("Akurasi menurut keramaian zona-provider")
            st.caption("Angka = perjalanan meleset per 100 · kelompok 1 paling ramai, kelompok 3 paling sepi yang dimodelkan")
            kel = D["penilaian_uji_per_kelompok"].rename(columns={"Unnamed: 0": "Kelompok"})
            kel = kel[["Kelompok", "Model", "Rata-rata 4 pekan", "Angka pekan lalu", "Kesimpulan"]]
            sel = kel["Rata-rata 4 pekan"] - kel["Model"]
            kel_t = kel.rename(columns={"Model": "Model LightGBM", "Rata-rata 4 pekan": "Rata-rata 4 pekan terakhir",
                                        "Angka pekan lalu": "Meniru pekan lalu"})
            st.dataframe(tabel(kel_t, desimal={"Model LightGBM": 1, "Rata-rata 4 pekan terakhir": 1, "Meniru pekan lalu": 1}),
                         hide_index=True, width="stretch")
            bacaan(
                "Angka yang sama, tetapi **dipisah menurut keramaian**. Setiap zona-provider (misalnya LaGuardia–Uber) "
                "dimasukkan ke salah satu kelompok: **kelompok 1 berisi yang paling ramai**, kelompok 3 yang paling sepi di "
                "antara yang dimodelkan.",
                f"Model lebih sedikit meleset di **{int((sel >= 1).sum())} dari {len(kel)} kelompok**. Beda terbesar ada di "
                f"{kel.loc[sel.idxmax(), 'Kelompok'].lower()}: model meleset {des(sel.max())} perjalanan lebih sedikit dari "
                f"setiap 100. **Makin sepi zonanya, makin besar persentase melesetnya**, dari {des(kel['Model'].iloc[0])} di "
                f"kelompok pertama menjadi {des(kel['Model'].iloc[-1])} di kelompok terakhir.",
                "Model yang unggul di setiap kelompok berarti keunggulannya **tidak hanya berasal dari zona yang ramai**. Satu "
                "model dipakai untuk semua zona-provider, sehingga **zona yang sepi ikut belajar dari pola zona yang ramai**. "
                "Persentase meleset yang lebih besar di zona sepi terjadi pada cara apa pun: bila dalam satu jam biasanya hanya "
                "ada 5 perjalanan, selisih 2 perjalanan saja sudah berarti meleset 40%. **Jumlah yang kecil lebih mudah "
                "dipengaruhi kebetulan.**")
    if D["penilaian_per_jarak"] is not None:
        with kanan, kartu():
            st.subheader("Akurasi menurut seberapa jauh ke depan perkiraan dibuat")
            st.caption("Angka = perjalanan meleset per 100 · semua model dilatih sampai Desember 2025 agar adil dibandingkan")
            j = D["penilaian_per_jarak"][["Jarak", "Model", "Rata-rata 4 pekan", "Angka k hari lalu"]]
            naik_m = j["Model"].iloc[-1] - j["Model"].iloc[0]
            naik_k = j["Angka k hari lalu"].iloc[-1] - j["Angka k hari lalu"].iloc[0]
            g0 = j["Rata-rata 4 pekan"].iloc[0] - j["Model"].iloc[0]
            g1 = j["Rata-rata 4 pekan"].iloc[-1] - j["Model"].iloc[-1]
            j_t = j.assign(Jarak=j["Jarak"].map(model_ke_depan)).rename(columns={
                "Jarak": "Perkiraan untuk", "Model": "Model LightGBM", "Rata-rata 4 pekan": "Rata-rata 4 pekan terakhir",
                "Angka k hari lalu": "Meniru 7, 14, atau 28 hari sebelumnya"})
            st.dataframe(tabel(j_t, desimal={c: 2 for c in j_t.columns[1:]}), hide_index=True, width="stretch")
            bacaan(
                "Seberapa sering perkiraan salah bila dibuat **7, 14, atau 28 hari sebelum hari yang diperkirakan**. Makin "
                "jauh ke depan, **makin lama data terbaru yang tersedia**: untuk perkiraan 28 hari ke depan, data paling baru "
                "adalah 4 pekan sebelumnya. Kolom terakhir adalah cara tanpa model yang meniru jumlah perjalanan pada jam yang "
                "sama 7, 14, atau 28 hari sebelumnya, sesuai barisnya.",
                f"Dari 7 ke 28 hari ke depan, model hanya meleset **{des(naik_m)} perjalanan lebih banyak dari setiap 100**, "
                f"sedangkan cara meniru hari sebelumnya meleset {des(naik_k)} lebih banyak. **Selisih dengan cara rata-rata "
                f"4 pekan justru melebar**, dari {des(g0)} per 100 untuk 7 hari ke depan menjadi {des(g1)} per 100 untuk 28 "
                "hari ke depan.",
                "Pola permintaan dari pekan ke pekan **sangat stabil**: jumlah perjalanan 4 pekan sebelumnya hampir sama "
                "miripnya dengan pekan lalu (tingkat kemiripan 0,88 dibanding 0,93 dari skala 0 sampai 1). Model mengandalkan "
                "pola rata-rata beberapa pekan, yang tidak banyak berubah walau datanya lebih lama. Cara meniru satu hari saja "
                "lebih cepat memburuk, karena satu hari lebih mudah dipengaruhi kebetulan. Artinya perkiraan untuk 4 pekan ke "
                "depan **masih layak dipakai untuk jadwal shift dan program insentif**.")

    if D["cakupan_rentang_bergulir"] is not None:
        with kartu():
            st.subheader("Seberapa sering jumlah sebenarnya berada di antara batas bawah dan batas atas, per bulan")
            st.caption("Diuji pada Januari–Mei 2026 · target 80%, artinya 8 dari 10 kali")
            c = D["cakupan_rentang_bergulir"]
            c = c[~c["Bulan"].astype(str).str.startswith("Batas")].copy()
            ing = {"Jan": "Januari", "Feb": "Februari", "Mar": "Maret", "Apr": "April", "May": "Mei", "Jun": "Juni",
                   "Jul": "Juli", "Aug": "Agustus", "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "Desember"}
            c["Bulan"] = c["Bulan"].astype(str).map(
                lambda b: " ".join(ing.get(x, x) for x in b.split(" ")).replace("Gabungan Jan–Mei", "Gabungan Januari–Mei"))
            bulanan = c[~c["Bulan"].str.startswith("Gabungan")].set_index("Bulan")
            gab = c[c["Bulan"].str.startswith("Gabungan")].iloc[0]
            c_t = c.rename(columns=NAMA_TINGKAT)
            st.dataframe(tabel(c_t, persen_kol={k: 1 for k in c_t.columns[1:]}), hide_index=True, width="stretch")
            kd = "Kota per hari"
            posisi = lambda v: "di bawah" if v < 78 else "di atas" if v > 82 else "sekitar"
            bacaan(
                "**Berapa persen jumlah perjalanan sebenarnya jatuh di antara batas bawah dan batas atas**, untuk setiap bulan "
                "Januari–Mei 2026. Setiap bulan diuji dengan batas yang disusun dari data sebelum bulan itu, **seperti saat "
                "dipakai sungguhan**. Kolom menunjukkan tingkat rincian, dari satu zona-provider per jam sampai seluruh kota per "
                "hari. **Targetnya 80%.**",
                f"Secara gabungan, {des(gab['Seri per jam'])}% jam di tingkat zona-provider ({posisi(gab['Seri per jam'])} "
                f"target) dan {des(gab[kd])}% hari di tingkat seluruh kota ({posisi(gab[kd])} target) berada di antara kedua "
                f"batas. **Hasilnya berbeda jauh antar bulan**: {bulanan[kd].idxmin()} paling rendah ({des(bulanan[kd].min())}% "
                f"hari), {bulanan[kd].idxmax()} paling tinggi ({des(bulanan[kd].max())}%).",
                "Bulan dengan **hari-hari anjlok ekstrem**, misalnya karena cuaca atau kejadian besar, membuat jumlah sebenarnya "
                "jatuh jauh di bawah batas bawah, dan **data cuaca serta kejadian tidak tersedia** untuk memperkirakannya. "
                "Setelah hari-hari itu ikut masuk ke data penyusun batas, jarak antara batas bawah dan atas menjadi lebih lebar, "
                "sehingga di bulan normal berikutnya jumlah sebenarnya lebih sering berada di antaranya. **Tingkat seluruh kota "
                "paling terdampak**, karena satu kejadian besar memengaruhi semua zona sekaligus. **Angka perkiraan utama tetap "
                "dapat dipercaya**; batas bawah dan atas dibaca sebagai **kisaran dalam kondisi normal**, bukan jaminan 80% "
                "dalam segala kondisi.")


# ================================================================
# Tab 6: Tentang
# ================================================================
with t_tentang:
    # Angka ringkasan diambil dari data penilaian, agar sama dengan tab Keandalan model
    _u = D["penilaian_uji"]
    if _u is not None:
        _u = _u.rename(columns={_u.columns[0]: "Cara"})
        _m, _p = _u.iloc[0], _u.loc[_u["Cara"] == "Rata-rata 4 pekan"].iloc[0]
        T_MELESET, T_TEPAT = des(_m["WMAPE"]), des(100 - _m["WMAPE"], 0)
        T_LEBIH = des((1 - _m["WMAPE"] / _p["WMAPE"]) * 100, 0)
        T_PB4 = des(_p["WMAPE"])
        T_BIAS = f"{des(abs(_m['Bias %']))}% {'lebih rendah' if _m['Bias %'] < 0 else 'lebih tinggi'}"
    else:
        T_MELESET, T_TEPAT, T_LEBIH, T_PB4, T_BIAS = "16,0", "84", "14", "18,5", "1,4% lebih rendah"
    st.markdown(f"""
#### Data
**NYC TLC High Volume For-Hire Vehicle Trip Records**, Januari 2024 – Mei 2026: **589.055.372 perjalanan** Uber dan Lyft
di **263 zona penjemputan**. Waktu adalah **waktu lokal New York**.

#### Dashboard
**Ringkasan temuan analisis bisnis**: pertumbuhan permintaan, jam dan hari paling ramai, zona paling ramai, pembagian
Uber dan Lyft, serta perubahan tarif dan pendapatan pengemudi. Kartu angka dan tabel tarif membandingkan periode yang
dipilih dengan **bulan yang sama setahun sebelumnya**, agar tidak tercampur musim.

#### Yang diperkirakan
**Jumlah perjalanan setiap jam, untuk setiap kombinasi zona dan provider** (misalnya LaGuardia–Uber), {MULAI.day} –
{tgl(AKHIR, hari=False)}. Setiap kombinasi zona dan provider disebut **seri**. Jumlah perjalanan per zona per jam per provider adalah **KPI utama project**, karena angka inilah yang langsung menentukan berapa armada dibutuhkan, kapan, dan di mana.

#### Cara
**Satu model LightGBM** untuk **359 seri yang menampung 95% permintaan**. Model ini dipilih dari beberapa kandidat
setelah **diuji pada tiga periode berbeda**. 165 seri sisanya sangat sepi, sehingga diperkirakan dengan rata-rata jam
yang sama 4 pekan terakhir. **Informasi yang dipakai model**: jumlah perjalanan pada jam yang sama 1–4 pekan
sebelumnya, rata-rata dan nilai tengahnya, tingkat permintaan terbaru, hari, jam, dan hari libur.

#### Seberapa jauh ke depan
**Pekan pertama** (1–7 Juni) memakai model yang hanya boleh melihat data sampai **7 hari sebelumnya**. **Pekan kedua**
memakai model untuk **14 hari ke depan**, **pekan ketiga dan keempat** memakai model untuk **28 hari ke depan**. Makin
jauh ke depan, makin lebar kisaran perkiraannya.

#### Istilah
| Istilah | Artinya |
|---|---|
| **Meleset per 100 perjalanan** | Dari setiap 100 perjalanan yang benar-benar terjadi, berapa yang tidak tertebak. {T_MELESET} berarti tepat sekitar {T_TEPAT}% |
| **Kesalahan X% lebih sedikit** | Perbandingan dua cara. Contoh: {T_MELESET} dibanding {T_PB4} berarti kesalahan model {T_LEBIH}% lebih sedikit, **bukan** akurasi {T_LEBIH}% |
| **Batas bawah dan batas atas** | Kisaran jumlah perjalanan. Dalam kondisi normal, 8 dari 10 kali jumlah sebenarnya berada di antaranya |
| **Seri** | Satu kombinasi zona dan provider, misalnya LaGuardia–Uber |
| **Model 7 hari ke depan** | Model yang membuat perkiraan paling lambat 7 hari sebelum hari yang diperkirakan |

#### Keputusan bisnis
| Temuan | Keputusan |
|---|---|
| 10 zona teratas hanya menampung **12,9%** perjalanan; butuh **58 zona** untuk separuhnya | **Armada direncanakan per zona, bukan untuk seluruh kota sekaligus** |
| Zona terbagi tiga kelompok menurut jam paling ramainya: pagi, sore, dan malam | **Jadwal armada berbeda untuk setiap kelompok zona**; pola jam rata-rata seluruh kota hanya cocok untuk 42% zona |
| Jumat dan Sabtu malam **2,3–2,6 kali** lebih ramai dari malam Senin–Kamis; Sabtu **36%** lebih ramai dari Senin | **Akhir pekan untuk perencanaan dan insentif adalah Jumat–Sabtu**, bukan Sabtu–Minggu |
| Stasiun dan bandara menerima hingga **22% lebih banyak** penumpang daripada yang berangkat dari sana | **Perkiraan permintaan perlu dibaca bersama arah perpindahan mobil** antar zona |
| Memakai rata-rata per zona per jam meleset **28 dari 100** perjalanan dan menebak **5,9% terlalu rendah** | **Perencanaan membutuhkan model** yang menangkap pola mingguan dan pertumbuhan |

#### Keputusan modelling
| Keputusan | Alasan |
|---|---|
| **Perkiraan hingga 7 hari ke depan**; model hanya memakai data paling baru 7 hari sebelumnya | Sesuai perencanaan armada mingguan, dan tidak memakai informasi yang belum tersedia saat perkiraan dibuat |
| **359 seri dimodelkan**, 165 seri sisanya memakai rata-rata 4 pekan | 359 seri itu menampung 95% permintaan; seri sisanya hampir selalu tanpa perjalanan |
| **Satu model LightGBM untuk semua seri** | **Paling sedikit meleset dan hasilnya stabil** di tiga periode uji; model terpisah per provider atau per kelompok tidak lebih baik |
| **Tanpa informasi urutan hari** (hari ke-1, ke-2, dan seterusnya sejak awal data) | Membuat perkiraan **7,2% terlalu tinggi**, karena model membawa tingkat permintaan musim ramai ke bulan yang lebih sepi |
| **Dibandingkan dengan cara tanpa model**: rata-rata 4 pekan terakhir dan meniru pekan lalu | Model hanya berguna bila **lebih sedikit meleset** daripada cara yang bisa dipakai tanpa model |
| **Batas bawah dan atas disusun dari 14 bulan catatan kesalahan** | **Diuji per bulan** pada Januari–Mei 2026, seperti saat dipakai sungguhan |

#### Rekomendasi bisnis
| Rekomendasi | Dasar bukti | Ukuran keberhasilan | Status sekarang |
|---|---|---|---|
| **1. Rencanakan armada dengan perkiraan per zona dan jam, bukan rata-rata** | Rata-rata per zona per jam meleset 28 dari 100; meniru pekan lalu saja sudah menurunkannya menjadi 22 | Meleset di bawah 22,1 per 100, pada seluruh seri dan di setiap kelompok seri | **Tercapai.** Model meleset {T_MELESET} per 100, dan lebih sedikit meleset di setiap kelompok seri |
| **2. Bedakan hari dan kelompok zona dalam perencanaan** | Jumat–Sabtu berbeda dari hari lain; zona terbagi kelompok pagi, sore, dan malam | Kesalahan pada Sabtu dan pada zona kelompok malam turun paling besar | **Diterapkan.** Hari, malam Jumat–Sabtu, dan kelompok jam zona dipakai sebagai informasi model |
| **3. Perhitungkan arah perpindahan mobil** | Stasiun dan bandara menerima hingga **22% lebih banyak** penumpang daripada yang berangkat dari sana | Penempatan armada memperhitungkan zona asal dan zona tujuan | **Belum.** Model baru memperkirakan penjemputan; arah perpindahan menjadi pengembangan berikutnya |

#### Rekomendasi modelling
1. **Pakai perkiraan 7 hari ke depan untuk menempatkan armada pekan depan.** Model meleset **{T_MELESET} dari 100** perjalanan (tepat sekitar {T_TEPAT}%), dan **kesalahannya {T_LEBIH}% lebih sedikit** daripada rata-rata 4 pekan terakhir, di setiap kelompok zona dan di jam sibuk.
2. **Siapkan armada sampai batas atas di jam dan zona yang mahal bila kekurangan pengemudi**, misalnya Jumat–Sabtu malam dan bandara. Secara keseluruhan perkiraan model **{T_BIAS}** dari kenyataan.
3. **Pakai perkiraan 14–28 hari ke depan untuk jadwal shift dan program insentif.** Model hanya meleset **0,6 perjalanan lebih banyak dari setiap 100** dibanding perkiraan 7 hari ke depan.
4. **Latih ulang model setiap 3 bulan, bukan setiap bulan.** Melatih ulang setiap bulan hanya mengurangi kesalahan **0,04 perjalanan dari setiap 100**.
5. **Pantau kesalahan setiap bulan.** Bila model tidak lagi lebih sedikit meleset daripada rata-rata 4 pekan terakhir, latih ulang lebih awal.
6. **Tambahkan data cuaca dan kejadian besar.** Hari anjlok ekstrem adalah **sumber kesalahan terbesar** dan penyebab batas bawah–atas kurang tepat di Januari–Februari.
7. **Siapkan pengaturan model tersendiri untuk perkiraan 14 dan 28 hari ke depan.** Saat ini keduanya memakai pengaturan model 7 hari.

#### Batas
- **Hanya perjalanan yang terlaksana yang tercatat**, sehingga yang diperkirakan adalah **permintaan yang terlayani**, bukan seluruh orang yang ingin memesan
- **Tidak ada data cuaca dan kejadian**, sehingga **hari anjlok ekstrem tidak dapat diperkirakan**
- **Data TLC dirilis sekitar dua bulan setelah bulannya berakhir**; perkiraan ini adalah **demonstrasi kemampuan model**, bukan perkiraan operasional langsung
""")
