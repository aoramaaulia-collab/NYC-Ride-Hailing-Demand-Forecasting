"""
Menyiapkan data untuk aplikasi Streamlit (dashboard + perkiraan).

Membaca:
  - output/final/hourly_demand_2024_2026.parquet     -> Dashboard dan data nyata terakhir
  - output/final/business_pickup_2024_2026.parquet   -> tabel tarif dan pendapatan pengemudi
  - output/model/*                                     -> hasil notebook 05_modelling
Menulis file kecil ke app/data. Dijalankan sekali, dan diulang setiap ada perkiraan baru.

Cara menjalankan, dari folder project:
    python siapkan_data_app.py
atau:
    python siapkan_data_app.py "/path/ke/project"
"""
import shutil
import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/auliaaorama/Project/Ride hailing")
FINAL = ROOT / "output" / "final"
MODEL = ROOT / "output" / "model"
PERMINTAAN = FINAL / "hourly_demand_2024_2026.parquet"
BISNIS = FINAL / "business_pickup_2024_2026.parquet"
KELUAR = ROOT / "app" / "data"
PEKAN_RIWAYAT = 8
NAMA_PROVIDER = {"HV0003": "Uber", "HV0005": "Lyft"}


def cek_ada(path):
    if not path.exists():
        sys.exit(f"File tidak ditemukan: {path}")
    return path


def cari_kolom(kolom, kandidat):
    for k in kandidat:
        if k in kolom:
            return k
    return None


KELUAR.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
con.execute("SET TimeZone = 'UTC'")      # waktu lokal New York yang tersimpan dibaca apa adanya
print(f"Project : {ROOT}\nKeluaran: {KELUAR}\n")

# ================================================================
# 1. Informasi seri dan zona
# ================================================================
seri = pd.read_parquet(cek_ada(MODEL / "seri_info.parquet"))
seri["provider"] = seri["provider"].astype(str)
seri["nama_zona"] = seri["nama_zona"].fillna("—").astype(str)
seri["borough"] = seri["borough"].fillna("Unknown").astype(str)
seri = seri[["provider", "zona", "nama_zona", "borough", "kelompok_seri", "dimodelkan", "kelompok_jam"]]
seri.to_parquet(KELUAR / "seri.parquet", index=False)
zona = seri.drop_duplicates("zona")[["zona", "nama_zona", "borough"]]
con.register("zona_df", zona)
print(f"seri.parquet                : {len(seri)} seri, {len(zona)} zona")

# ================================================================
# 2. Dashboard: ringkasan permintaan per bulan, per jam × hari, per zona
# ================================================================
kolom_p = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{cek_ada(PERMINTAAN)}')").df()["column_name"].tolist()
JAM = cari_kolom(kolom_p, ["request_hour", "jam", "pickup_hour"])
PROV = cari_kolom(kolom_p, ["provider", "provider_name", "hvfhs_license_num"])
ZONA = cari_kolom(kolom_p, ["pickup_location_id", "PULocationID", "zona"])
DEM = cari_kolom(kolom_p, ["demand", "total_trips", "trips"])
if None in (JAM, PROV, ZONA, DEM):
    sys.exit(f"Kolom file permintaan tidak dikenali: {kolom_p}")
prov_sql = f"CASE CAST({PROV} AS VARCHAR) WHEN 'HV0003' THEN 'Uber' WHEN 'HV0005' THEN 'Lyft' ELSE CAST({PROV} AS VARCHAR) END"
con.execute(f"""
CREATE OR REPLACE VIEW permintaan AS
SELECT CAST({JAM} AS TIMESTAMP) AS jam, {prov_sql} AS provider, CAST({ZONA} AS INTEGER) AS zona,
       CAST({DEM} AS DOUBLE) AS demand
FROM read_parquet('{PERMINTAAN}')
""")

con.execute("""
COPY (
    SELECT date_trunc('month', p.jam) AS bulan, p.provider, COALESCE(z.borough, 'Unknown') AS borough,
           SUM(p.demand) AS perjalanan
    FROM permintaan p LEFT JOIN zona_df z USING (zona)
    GROUP BY ALL ORDER BY ALL
) TO '{}' (FORMAT PARQUET)""".format(KELUAR / "dash_bulanan.parquet"))
con.execute("""
COPY (
    SELECT date_trunc('month', p.jam) AS bulan, p.provider, COALESCE(z.borough, 'Unknown') AS borough,
           isodow(p.jam) AS hari, hour(p.jam) AS jam_hari, SUM(p.demand) AS perjalanan
    FROM permintaan p LEFT JOIN zona_df z USING (zona)
    GROUP BY ALL ORDER BY ALL
) TO '{}' (FORMAT PARQUET)""".format(KELUAR / "dash_jam.parquet"))
con.execute("""
COPY (
    SELECT date_trunc('month', jam) AS bulan, provider, zona, SUM(demand) AS perjalanan
    FROM permintaan GROUP BY ALL ORDER BY ALL
) TO '{}' (FORMAT PARQUET)""".format(KELUAR / "dash_zona.parquet"))
total = con.execute("SELECT SUM(demand), MIN(jam), MAX(jam) FROM permintaan").fetchone()
print(f"dash_bulanan/jam/zona       : {total[0]:,.0f} perjalanan, {total[1]:%b %Y} – {total[2]:%b %Y}")

# ================================================================
# 3. Dashboard: tarif dan pendapatan pengemudi (bila kolomnya tersedia)
# ================================================================
PERLU = ["total_base_fare", "total_trip_miles", "total_trip_seconds", "total_driver_pay", "valid_fare_trips"]
if BISNIS.exists():
    kolom_b = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{BISNIS}')").df()["column_name"].tolist()
    JAM_B = cari_kolom(kolom_b, ["request_hour", "pickup_hour", "jam", "pickup_date", "tanggal"])
    PROV_B = cari_kolom(kolom_b, ["provider", "provider_name", "hvfhs_license_num"])
    ZONA_B = cari_kolom(kolom_b, ["pickup_location_id", "PULocationID", "zona"])
    TRIP_B = cari_kolom(kolom_b, ["total_trips", "demand", "trips"])
    kurang = [k for k in PERLU if k not in kolom_b]
    if kurang or None in (JAM_B, PROV_B, ZONA_B, TRIP_B):
        print(f"dash_tarif.parquet          : DILEWATI — kolom tidak dikenali. Tersedia: {kolom_b}")
    else:
        prov_b = f"CASE CAST({PROV_B} AS VARCHAR) WHEN 'HV0003' THEN 'Uber' WHEN 'HV0005' THEN 'Lyft' ELSE CAST({PROV_B} AS VARCHAR) END"
        con.execute(f"""
        COPY (
            SELECT date_trunc('month', CAST(b.{JAM_B} AS TIMESTAMP)) AS bulan, {prov_b} AS provider,
                   COALESCE(z.borough, 'Unknown') AS borough,
                   SUM(b.{TRIP_B}) AS perjalanan, SUM(b.total_base_fare) AS tarif, SUM(b.valid_fare_trips) AS perjalanan_tarif,
                   SUM(b.total_trip_miles) AS mil, SUM(b.total_trip_seconds) AS detik, SUM(b.total_driver_pay) AS pendapatan
            FROM read_parquet('{BISNIS}') b LEFT JOIN zona_df z ON z.zona = CAST(b.{ZONA_B} AS INTEGER)
            GROUP BY ALL ORDER BY ALL
        ) TO '{KELUAR / "dash_tarif.parquet"}' (FORMAT PARQUET)""")
        print("dash_tarif.parquet          : dibuat")
else:
    print(f"dash_tarif.parquet          : DILEWATI — {BISNIS.name} tidak ada")

# ================================================================
# 4. Perkiraan per seri per jam: 7, 14, 28 hari digabung.
#    Hari 1–7 dari model 7 hari, hari 8–14 dari model 14 hari, hari 15–28 dari model 28 hari.
# ================================================================
KOLOM_PERKIRAAN = ["jam", "zona", "provider", "batas_bawah", "perkiraan", "batas_atas"]
bagian = []
for jarak, nama_file in [(7, "perkiraan_seri_per_jam.csv"), (14, "perkiraan_seri_per_jam_14hari.csv"),
                         (28, "perkiraan_seri_per_jam_28hari.csv")]:
    path = MODEL / nama_file
    if not path.exists():
        if jarak == 7:
            cek_ada(path)
        print(f"  (lewati jarak {jarak} hari: {nama_file} tidak ada)")
        continue
    d = pd.read_csv(path, usecols=KOLOM_PERKIRAAN, parse_dates=["jam"])
    d["provider"] = d["provider"].astype(str)
    d["jarak"] = jarak
    bagian.append(d)
p = pd.concat(bagian, ignore_index=True)
MULAI = p.loc[p["jarak"] == 7, "jam"].min().normalize()
hari_ke = (p["jam"].dt.normalize() - MULAI).dt.days + 1
p = p[(hari_ke >= p["jarak"].map({7: 1, 14: 8, 28: 15})) & (hari_ke <= p["jarak"])].copy()
p = p.merge(seri[["provider", "zona", "dimodelkan"]], on=["provider", "zona"], how="left")
p["cara"] = p["dimodelkan"].map({True: "Model", False: "Rata-rata 4 pekan"}).fillna("Model")
p = p.drop(columns=["dimodelkan"]).sort_values(["provider", "zona", "jam"])
for k in ["batas_bawah", "perkiraan", "batas_atas"]:
    p[k] = p[k].astype("float32")
p.to_parquet(KELUAR / "perkiraan_seri.parquet", index=False)
print(f"perkiraan_seri.parquet      : {len(p):,} baris, {p['jam'].min():%d %b} – {p['jam'].max():%d %b %Y}")

# ================================================================
# 5. Perkiraan seluruh kota (dikalibrasi pada tingkat kota di notebook)
# ================================================================
if (MODEL / "perkiraan_kota_juni_per_hari.csv").exists():
    kh = pd.read_csv(MODEL / "perkiraan_kota_juni_per_hari.csv", parse_dates=["tanggal"])
else:
    kh = pd.read_csv(cek_ada(MODEL / "perkiraan_kota_per_hari.csv"))
    kh = kh[kh["tanggal"] != "Total 7 hari"].copy()
    kh["tanggal"] = pd.to_datetime(kh["tanggal"], format="%d %b %Y")
    kh["model"] = "7 hari"
kh[["tanggal", "batas_bawah", "perkiraan", "batas_atas", "model"]].to_parquet(KELUAR / "kota_harian.parquet", index=False)
kj = pd.read_csv(cek_ada(MODEL / "perkiraan_kota_per_jam.csv"), parse_dates=["jam"])
kj[["jam", "batas_bawah", "perkiraan", "batas_atas"]].to_parquet(KELUAR / "kota_per_jam.parquet", index=False)
print(f"kota_harian / kota_per_jam  : {len(kh)} hari / {len(kj)} jam")

# ================================================================
# 6. Data nyata terakhir, untuk disandingkan dengan perkiraan
# ================================================================
dari = MULAI - pd.Timedelta(weeks=PEKAN_RIWAYAT)
r = con.execute(f"""
    SELECT jam, provider, zona, SUM(demand) AS demand FROM permintaan
    WHERE jam >= TIMESTAMP '{dari}' AND jam < TIMESTAMP '{MULAI}'
    GROUP BY ALL
""").df()
r["demand"] = r["demand"].astype("float32")
r.to_parquet(KELUAR / "riwayat_seri.parquet", index=False)
r.groupby(r["jam"].dt.normalize())["demand"].sum().rename_axis("tanggal").reset_index() \
 .to_parquet(KELUAR / "riwayat_kota_harian.parquet", index=False)
rj = r.groupby("jam")["demand"].sum().reset_index()
rj[rj["jam"] >= MULAI - pd.Timedelta(days=14)].to_parquet(KELUAR / "riwayat_kota_per_jam.parquet", index=False)
print(f"riwayat_seri.parquet        : {len(r):,} baris, {r['jam'].min():%d %b} – {r['jam'].max():%d %b %Y}")

# ================================================================
# 7. Penilaian model
# ================================================================
for nama in ["penilaian_uji.csv", "penilaian_uji_per_kelompok.csv", "penilaian_per_jarak.csv",
             "cakupan_rentang_bergulir.csv", "perkiraan_kota_juni_per_pekan.csv"]:
    if (MODEL / nama).exists():
        shutil.copy(MODEL / nama, KELUAR / nama)
        print(f"{nama:28}: disalin")

ukuran = sum(f.stat().st_size for f in KELUAR.iterdir()) / 1e6
print(f"\nSelesai. Ukuran folder app/data: {ukuran:.1f} MB")
