# Ride-Hailing Demand and Operational Analytics with Demand Forecasting

## 1. Pendahuluan

### 1.1 Apa yang Dimaksud dengan Ride-Hailing?

Ride-hailing adalah layanan transportasi yang memungkinkan pengguna memesan kendaraan melalui aplikasi digital. Secara umum, proses layanan dimulai ketika pelanggan membuka aplikasi, menentukan lokasi penjemputan dan tujuan, kemudian mengirimkan permintaan perjalanan. Platform selanjutnya mencocokkan permintaan tersebut dengan driver yang tersedia, setelah itu driver menuju lokasi penjemputan, mengantar pelanggan, dan menyelesaikan perjalanan di lokasi tujuan.

Secara konseptual, layanan seperti Uber dan Lyft di Amerika Serikat memiliki karakteristik bisnis yang sejenis dengan layanan seperti GrabCar atau GoCar di Indonesia. Kesamaan tersebut terutama terletak pada mekanisme pemesanan berbasis aplikasi, pencocokan permintaan penumpang dengan driver, serta ketergantungan operasional terhadap keseimbangan antara jumlah permintaan perjalanan dan ketersediaan driver.

### 1.2 Apa itu Uber dan Lyft?

Uber dan Lyft adalah dua perusahaan penyedia layanan ride-hailing yang beroperasi di Amerika Serikat. Dalam dataset High Volume For-Hire Vehicle Trip Records (HVFHV) yang digunakan pada project ini, provider diidentifikasi menggunakan variabel `hvfhs_license_num`.

Pada pemeriksaan data Januari 2024 ditemukan dua kode provider:

| Provider Code | Provider | Jumlah Trip Januari 2024 |
|---|---|---:|
| HV0003 | Uber | 14.432.755 |
| HV0005 | Lyft | 5.231.175 |
| **Total** |  | **19.663.930** |

Dengan demikian, satu file HVFHV Januari 2024 tidak hanya mencatat perjalanan dari satu perusahaan, tetapi mencakup perjalanan dari beberapa provider ride-hailing.

Informasi provider tidak langsung dihapus pada tahap awal karena masih bermanfaat untuk historical business analytics, misalnya untuk membandingkan volume perjalanan, pola permintaan, waktu sibuk, maupun karakteristik perjalanan antara Uber dan Lyft. Keputusan apakah forecasting akan memodelkan seluruh provider atau hanya satu provider akan dilakukan setelah business scope dan pola data dipahami secara lebih lengkap.

---

## 2. Latar Belakang Project

Perusahaan ride-hailing beroperasi pada kondisi permintaan yang sangat dinamis. Jumlah permintaan perjalanan dapat berubah berdasarkan waktu, lokasi, hari dalam minggu, periode liburan, dan berbagai kondisi operasional lainnya. Pada suatu area, permintaan dapat relatif rendah pada siang hari tetapi meningkat tajam pada jam pulang kerja. Pada area lain, peningkatan permintaan dapat terjadi pada akhir pekan, malam hari, atau periode tertentu.

Perubahan permintaan tersebut menjadi tantangan operasional karena perusahaan perlu menjaga keseimbangan antara demand dari pelanggan dan supply layanan yang tersedia. Apabila peningkatan permintaan terjadi tanpa dapat diantisipasi, perusahaan berpotensi menghadapi ketidakseimbangan antara permintaan dan ketersediaan driver pada suatu area dan waktu tertentu.

Selain persoalan demand, perusahaan juga perlu memahami performa historis bisnis dan operasionalnya. Informasi seperti jumlah perjalanan, pola perjalanan berdasarkan waktu, lokasi pickup dan drop-off, jarak dan durasi perjalanan, tarif penumpang, pembayaran kepada driver, shared ride, serta layanan kendaraan aksesibel dapat memberikan gambaran mengenai karakteristik aktivitas ride-hailing.

Oleh karena itu, project ini dirancang menggunakan dua pendekatan analitik yang saling melengkapi:

1. **Historical Business Analytics**, untuk memahami apa yang telah terjadi pada aktivitas ride-hailing.
2. **Demand Forecasting**, untuk memperkirakan apa yang kemungkinan akan terjadi pada periode berikutnya.

Dengan pendekatan tersebut, project tidak berhenti pada pembuatan model prediksi. Hasil akhirnya diharapkan dapat memberikan historical insight melalui dashboard sekaligus future demand signal melalui forecasting application.

---

## 3. Business Problem

Project ini menggunakan sudut pandang stakeholder **Operations / Marketplace Team** pada perusahaan ride-hailing.

### 3.1 Business Problem 1 — Historical Performance

Stakeholder membutuhkan pemahaman mengenai pola perjalanan yang telah terjadi untuk menjawab beberapa pertanyaan seperti:

- Bagaimana perkembangan jumlah perjalanan dari waktu ke waktu?
- Pada jam dan hari apa jumlah ride request paling tinggi?
- Pickup zone mana yang menghasilkan volume perjalanan terbesar?
- Bagaimana perbedaan pola weekday dan weekend?
- Bagaimana perbedaan karakteristik perjalanan antar-provider?
- Bagaimana karakteristik jarak dan durasi perjalanan?
- Bagaimana pola passenger fare dan driver pay?
- Bagaimana performa shared ride dan layanan wheelchair-accessible vehicle jika relevan?

Permasalahan ini akan dijawab melalui **Business Analytics Dashboard**.

### 3.2 Business Problem 2 — Future Demand

Historical analysis hanya menjelaskan aktivitas yang telah terjadi. Operations team juga membutuhkan indikasi mengenai kondisi yang kemungkinan akan terjadi beberapa jam berikutnya.

Business problem forecasting dirumuskan sebagai:

> **Bagaimana memperkirakan jumlah ride request pada setiap pickup zone dan periode waktu tertentu berdasarkan pola historis perjalanan?**

Forecast digunakan untuk mengidentifikasi:

- area yang diperkirakan mengalami high demand;
- waktu yang diperkirakan mengalami high demand;
- besarnya perubahan forecast dibandingkan typical historical demand.

Hasil model diposisikan sebagai **input atau early signal untuk driver supply planning**, bukan sebagai model yang menentukan jumlah driver optimal. Penentuan jumlah driver optimal membutuhkan supply-side variables yang tidak tersedia lengkap pada dataset ini.

---

## 4. Tujuan Project

### 4.1 General Objective

Menganalisis pola bisnis dan operasional layanan ride-hailing serta membangun model forecasting untuk memperkirakan permintaan perjalanan berdasarkan waktu dan lokasi.

### 4.2 Specific Objectives

Project bertujuan untuk:

1. Menganalisis perkembangan jumlah perjalanan berdasarkan waktu.
2. Mengidentifikasi jam, hari, dan periode dengan jumlah permintaan tinggi.
3. Mengidentifikasi pickup zone dan drop-off zone dengan volume perjalanan tinggi.
4. Menganalisis karakteristik perjalanan berdasarkan jarak, durasi, waktu, dan lokasi.
5. Mengevaluasi indikator finansial seperti passenger fare dan driver pay.
6. Membandingkan pola perjalanan antar-provider apabila relevan terhadap business analysis.
7. Membentuk dataset forecasting pada tingkat **pickup zone × hour**.
8. Mengembangkan baseline dan beberapa kandidat forecasting model.
9. Mengevaluasi model menggunakan chronological validation dan forecasting metrics.
10. Menghasilkan future demand prediction yang dapat digunakan sebagai early signal untuk supply planning.
11. Menyajikan historical business insight melalui dashboard.
12. Menyajikan forecasting output melalui aplikasi deployment.

---

## 5. Dataset yang Digunakan

Dataset utama adalah **High Volume For-Hire Vehicle Trip Records (HVFHV)** yang dipublikasikan oleh New York City Taxi and Limousine Commission (NYC TLC).

Setiap baris pada raw dataset merepresentasikan **satu perjalanan**.

Secara sederhana, satu perjalanan dapat digambarkan sebagai:

```text
Customer mengirim ride request
        ↓
Driver menuju lokasi pickup
        ↓
Driver tiba di area pickup
        ↓
Customer dijemput
        ↓
Perjalanan berlangsung
        ↓
Customer sampai tujuan
```

Aktivitas tersebut menghasilkan informasi mengenai provider, waktu request, pickup, drop-off, lokasi, jarak, durasi, fare, driver pay, shared ride, dan atribut lainnya.

---

## 6. Periode Data Project

### 6.1 Periode Final

Project final dirancang menggunakan data:

**Januari 2024 sampai Mei 2026**

atau sekitar **29 bulan data**:

- 12 bulan pada 2024;
- 12 bulan pada 2025;
- 5 bulan pada 2026.

### 6.2 Mengapa Saat Ini Hanya Januari 2024 yang Diperiksa?

Januari 2024 **bukan keseluruhan dataset project**.

File Januari 2024 digunakan sebagai **pilot data / pipeline validation sample** untuk:

- memahami struktur raw data;
- memahami arti setiap kolom;
- memeriksa data quality;
- memvalidasi provider;
- memvalidasi timestamp dan location ID;
- menentukan cleaning rules;
- menguji proses transformation;
- memastikan pipeline dapat dijalankan dengan benar sebelum diterapkan ke seluruh 29 bulan.

Hal ini penting karena Januari 2024 saja memiliki **19.663.930 perjalanan**. Apabila pipeline langsung dijalankan ke seluruh periode tanpa validasi awal dan kemudian ditemukan kesalahan, seluruh proses harus diulang pada data yang jauh lebih besar.

Setelah pipeline Januari 2024 dinyatakan benar, prosedur yang sama akan diterapkan secara otomatis pada Februari 2024, Maret 2024, dan seterusnya hingga Mei 2026.

---

## 7. Data Understanding: Penjelasan Variabel

Raw dataset yang diperiksa memiliki 24 kolom. Variabel tersebut dapat dikelompokkan berdasarkan fungsi bisnisnya.

### 7.1 Provider dan Dispatch

| Kolom | Arti | Potensi Penggunaan |
|---|---|---|
| `hvfhs_license_num` | Kode provider HVFHS | Provider comparison atau filtering |
| `dispatching_base_num` | Base yang melakukan dispatch kendaraan | Operational dispatch analysis |
| `originating_base_num` | Base yang menerima request awal | Source/base analysis |

Variabel yang paling relevan pada kelompok ini adalah `hvfhs_license_num` karena dapat digunakan untuk membedakan Uber dan Lyft.

### 7.2 Variabel Waktu

| Kolom | Arti | Relevansi |
|---|---|---|
| `request_datetime` | Waktu customer membuat ride request | Variabel utama untuk demand |
| `on_scene_datetime` | Waktu driver tiba di lokasi pickup | Operational timing |
| `pickup_datetime` | Waktu passenger benar-benar dijemput | Pickup/waiting analysis |
| `dropoff_datetime` | Waktu passenger sampai tujuan | Trip duration analysis |

Urutan proses perjalanan secara konseptual adalah:

```text
request_datetime
        ↓
on_scene_datetime
        ↓
pickup_datetime
        ↓
dropoff_datetime
```

Untuk forecasting demand, `request_datetime` menjadi timestamp utama karena demand muncul ketika customer mengirim request, bukan ketika customer akhirnya dijemput.

Contoh:

```text
08:01 → request
08:04 → request
08:12 → request
08:30 → request
```

Semua request antara 08:00–08:59 akan dihitung sebagai demand pada interval 08:00.

### 7.3 Variabel Lokasi

| Kolom | Arti | Relevansi |
|---|---|---|
| `PULocationID` | Pickup Location ID | Menentukan lokasi asal demand |
| `DOLocationID` | Drop-off Location ID | Menentukan lokasi tujuan |

Forecasting project membutuhkan `PULocationID` karena target tidak hanya menjawab **kapan demand meningkat**, tetapi juga **di area mana demand meningkat**.

Dengan demikian, unit utama forecasting menjadi:

> **Pickup Zone × Hour → Demand**

### 7.4 Karakteristik Perjalanan

| Kolom | Arti | Potensi Analisis |
|---|---|---|
| `trip_miles` | Jarak passenger trip | Average trip distance |
| `trip_time` | Lama perjalanan | Average trip duration |

Variabel tersebut berguna untuk historical dashboard, misalnya untuk melihat pola jarak dan durasi berdasarkan area, hari, jam, atau provider.

### 7.5 Variabel Finansial

| Kolom | Arti |
|---|---|
| `base_passenger_fare` | Tarif dasar passenger |
| `tolls` | Biaya toll |
| `bcf` | Black Car Fund |
| `sales_tax` | Pajak penjualan |
| `congestion_surcharge` | Congestion surcharge |
| `airport_fee` | Airport-related fee |
| `tips` | Tip |
| `driver_pay` | Pembayaran kepada driver |

Kelompok ini dapat digunakan untuk historical financial and operational analytics.

Namun, variabel seperti `trip_miles`, `trip_time`, `fare`, `tips`, dan `driver_pay` tidak boleh otomatis digunakan sebagai forecasting feature karena nilainya baru diketahui selama atau setelah perjalanan terjadi. Penggunaan future information tersebut berpotensi menyebabkan **data leakage**.

### 7.6 Shared Ride

| Kolom | Arti |
|---|---|
| `shared_request_flag` | Passenger meminta shared ride |
| `shared_match_flag` | Passenger benar-benar mendapat shared ride match |

Variabel ini dapat digunakan untuk menganalisis perbedaan antara shared ride request dan shared ride yang benar-benar berhasil matched.

### 7.7 Accessibility

| Kolom | Arti |
|---|---|
| `access_a_ride_flag` | Penanda trip terkait Access-A-Ride |
| `wav_request_flag` | Passenger meminta wheelchair-accessible vehicle |
| `wav_match_flag` | Request berhasil dilayani dengan WAV |

Kelompok ini dapat digunakan sebagai tambahan operational/service analytics apabila hasil exploratory analysis menunjukkan informasi yang cukup relevan.

---

## 8. Preliminary Data Quality Assessment — Januari 2024

Pemeriksaan awal dilakukan terhadap file Januari 2024 menggunakan DuckDB.

### 8.1 Jumlah Data dan Provider

Total raw data:

**19.663.930 rows**

Distribusi provider:

| Provider Code | Jumlah Trip | Proporsi Kira-kira |
|---|---:|---:|
| HV0003 — Uber | 14.432.755 | 73,4% |
| HV0005 — Lyft | 5.231.175 | 26,6% |

Hasil ini menunjukkan bahwa Uber memiliki volume perjalanan lebih besar pada file Januari 2024. Namun, provider belum difilter karena perbandingan provider masih berpotensi memberikan business insight.

### 8.2 Missing dan Invalid Values pada Variabel Forecasting Utama

| Quality Check | Jumlah |
|---|---:|
| Total rows | 19.663.930 |
| Missing `request_datetime` | 0 |
| Missing `PULocationID` | 0 |
| Invalid `PULocationID` | 0 |

Temuan ini menunjukkan bahwa variabel utama untuk membentuk demand forecasting relatif bersih pada Januari 2024.

Namun, kesimpulan data quality final belum dapat diberikan karena masih diperlukan pemeriksaan terhadap:

- missing value pada kolom lainnya;
- duplicate record;
- chronological consistency;
- nilai negatif atau tidak logis pada distance, duration, fare, dan driver pay;
- validitas categorical flags;
- konsistensi date range per monthly file.

Data quality assessment Januari 2024 digunakan untuk menyusun aturan cleaning yang nantinya diterapkan secara konsisten pada seluruh periode 2024–2026.

---

## 9. Data Pipeline dan Arsitektur Project

Karena project menggunakan **BigQuery Sandbox tanpa billing**, seluruh raw trip-level data tidak akan dimasukkan langsung ke BigQuery.

Raw data disimpan dan diproses secara lokal menggunakan DuckDB. Hasil transformation yang lebih kecil kemudian dimasukkan ke BigQuery sebagai analytical warehouse.

Arsitektur project menjadi:

```text
NYC TLC Monthly Parquet
Jan 2024 – May 2026
        ↓
DuckDB
        ↓
Data Understanding
Data Quality
Cleaning
Transformation
Aggregation
        ↓
Compact Analytical Tables
        ↓
BigQuery Sandbox
        ↓
SQL Analytical / Feature Mart
        ↓
        ├───────────────┐
        ↓               ↓
Business Dashboard   Python Forecasting
                        ↓
                   Model Evaluation
                        ↓
                  Forecast Results
                        ↓
                     Streamlit
```

Pendekatan ini dipilih agar project tetap dapat menggunakan SQL dan BigQuery sebagai bagian dari data pipeline tanpa harus menyimpan ratusan juta raw rows di BigQuery Sandbox.

---

## 10. Tabel yang Direncanakan di BigQuery

BigQuery dataset yang digunakan adalah:

`ride_hailing`

Di dalamnya akan dibuat beberapa analytical tables.

### 10.1 `mart_business_metrics`

Berisi hasil agregasi yang digunakan untuk dashboard historical analytics.

Contoh dimensi:

- date;
- month;
- hour;
- provider;
- pickup zone;
- drop-off zone.

Contoh metrics:

- total trips;
- average trip distance;
- average trip duration;
- total / average passenger fare;
- average driver pay;
- shared ride count;
- WAV request count.

Table ini dibuat dalam bentuk agregat agar sesuai dengan keterbatasan BigQuery Sandbox.

### 10.2 `hourly_demand`

Berisi time-series base:

| datetime | pickup_location_id | provider | demand |
|---|---:|---|---:|

`demand` adalah jumlah request pada kombinasi pickup zone dan satu jam tertentu.

### 10.3 `forecast_features`

Berisi dataset siap modeling seperti:

- datetime;
- pickup zone;
- demand;
- lag features;
- rolling features;
- calendar features;
- holiday features.

### 10.4 `forecast_results`

Berisi output final model:

- datetime;
- pickup zone;
- actual demand;
- predicted demand;
- model name;
- forecast horizon.

---

## 11. Historical Business Analytics

Historical analytics dirancang untuk menjawab **apa yang telah terjadi**.

### 11.1 Dashboard 1 — Executive Overview

KPI yang dapat ditampilkan:

- Total Trips
- Average Trips per Day
- Total / Average Passenger Fare
- Average Trip Distance
- Average Trip Duration
- Average Driver Pay

Visualisasi potensial:

- Monthly Trip Trend
- Daily Trip Trend
- Demand by Hour
- Provider Distribution
- Weekday vs Weekend

### 11.2 Dashboard 2 — Demand & Location Analysis

Fokus utama:

- Top Pickup Zones
- Top Drop-off Zones
- Demand by Hour
- Demand by Day
- Zone × Hour Heatmap
- Weekday vs Weekend Pattern
- Geographic pickup-demand distribution apabila Taxi Zone map tersedia

Dashboard ini menjadi jembatan utama antara historical analytics dan forecasting karena menunjukkan struktur spatial dan temporal demand.

### 11.3 Dashboard 3 — Operational & Financial Analysis

Analisis dapat mencakup:

- Average Fare by Zone
- Average Driver Pay
- Trip Distance
- Trip Duration
- Fare per Mile
- Airport-related metrics
- Shared Ride
- WAV Service

Tidak semua metric harus digunakan. KPI final akan dipilih setelah exploratory analysis menunjukkan mana yang benar-benar menghasilkan business insight.

---

## 12. Forecasting Dataset

Raw dataset memiliki bentuk:

> **1 row = 1 trip**

Untuk forecasting, data harus diubah menjadi:

> **1 row = 1 pickup zone × 1 hour**

Contoh:

| datetime | pickup_zone | demand |
|---|---:|---:|
| 2025-01-01 08:00 | 161 | 420 |
| 2025-01-01 09:00 | 161 | 510 |
| 2025-01-01 08:00 | 236 | 330 |

Target forecasting adalah:

`demand`

atau jumlah ride request pada area dan jam tertentu.

---

## 13. Forecasting Feature Engineering

Beberapa feature yang direncanakan:

### 13.1 Lag Features

- `lag_1` — demand satu jam sebelumnya
- `lag_2`
- `lag_3`
- `lag_24` — jam yang sama satu hari sebelumnya
- `lag_48`
- `lag_168` — jam yang sama satu minggu sebelumnya

### 13.2 Rolling Features

- rolling mean 3 jam
- rolling mean 6 jam
- rolling mean 24 jam
- rolling mean 168 jam
- rolling standard deviation

Rolling feature harus dibentuk hanya menggunakan informasi historical agar tidak menimbulkan target leakage.

### 13.3 Calendar Features

- hour
- day of week
- month
- weekend indicator
- holiday indicator

### 13.4 Spatial Feature

- pickup zone

Dengan feature tersebut, model tidak hanya mengetahui pola waktu tetapi juga perbedaan karakteristik demand antar-area.

---

## 14. Train, Validation, dan Test Strategy

Karena forecasting melibatkan urutan waktu, data tidak akan dibagi menggunakan random train-test split.

### 14.1 Development Split

**Training:** Januari 2024 – September 2025

**Validation:** Oktober 2025 – Desember 2025

Alasan validation ditempatkan pada akhir 2025 adalah untuk menguji kemampuan model menghadapi pola akhir tahun. Training tetap memiliki contoh periode akhir tahun dari Oktober–Desember 2024 sehingga seasonal pattern tersebut tidak sepenuhnya asing bagi model.

### 14.2 Final Retraining

Setelah model, feature, dan hyperparameter terbaik dipilih berdasarkan validation, model final dapat dilatih kembali menggunakan:

**Januari 2024 – Desember 2025**

### 14.3 Final Test

**Januari 2026 – Mei 2026**

Periode 2026 dipertahankan sebagai **unseen future data** dan tidak digunakan untuk memilih feature, model, atau hyperparameter.

Dengan demikian:

```text
DEVELOPMENT

Jan 2024 ───────── Sep 2025 | Oct ─ Dec 2025
          TRAIN              VALIDATION

FINAL

Jan 2024 ───────────────── Dec 2025 | Jan ─ May 2026
             RETRAIN                   TEST
```

---

## 15. Walk-Forward Validation

Selain satu validation block, model dapat dievaluasi dengan expanding-window / walk-forward validation.

Contoh:

```text
Fold 1
Train sampai Jun 2025
→ Validate Jul–Aug 2025

Fold 2
Train sampai Aug 2025
→ Validate Sep–Oct 2025

Fold 3
Train sampai Oct 2025
→ Validate Nov–Dec 2025
```

Pendekatan ini membuat model diuji pada beberapa kondisi waktu dan lebih menyerupai proses forecasting di production.

---

## 16. Forecasting Model Candidates

Project akan membandingkan model dari beberapa keluarga.

### 16.1 Baseline

- Naive Forecast
- Daily Seasonal Naive
- Weekly Seasonal Naive

Baseline diperlukan untuk membuktikan bahwa model kompleks benar-benar memberikan peningkatan.

### 16.2 Statistical Models

- Holt-Winters
- SARIMA
- SARIMAX

Cabang statistical model digunakan untuk menangkap struktur level, trend, autocorrelation, dan seasonality.

### 16.3 Machine Learning Models

- Linear Regression
- Random Forest
- XGBoost
- LightGBM
- CatBoost

Machine-learning models menggunakan lag, rolling, calendar, dan spatial features.

Model tidak akan dipilih berdasarkan jumlah algoritma yang dicoba, tetapi berdasarkan performa chronological validation dan relevansinya terhadap struktur data.

---

## 17. Forecast Evaluation Metrics

Metric utama:

### WMAPE

Digunakan sebagai primary metric karena demand antar-zone memiliki skala berbeda dan terdapat kemungkinan observasi dengan actual demand kecil.

Metric pendukung:

### MAE

Mengukur rata-rata absolute forecasting error dalam satuan ride request.

### RMSE

Memberikan penalti lebih besar terhadap forecasting error yang ekstrem.

MAPE dapat digunakan sebagai diagnostic metric pada actual demand non-zero, tetapi tidak menjadi metric utama.

---

## 18. Forecasting Deployment

Model final direncanakan untuk di-deploy menggunakan **Streamlit**.

Application dapat menyediakan input:

- Pickup Zone
- Forecast Date / Time
- Forecast Horizon

Contoh output:

| Hour | Predicted Demand |
|---|---:|
| 18:00 | 1.050 |
| 19:00 | 1.220 |
| 20:00 | 1.380 |
| 21:00 | 1.250 |

Selain angka forecast, aplikasi dapat membandingkan hasil tersebut dengan typical historical demand.

Contoh:

```text
Typical Demand  = 1,000
Forecast Demand = 1,380
Expected Uplift = +38%
```

Kemudian sistem dapat memberi status:

**High Demand Expected**

Aplikasi tidak secara langsung menentukan jumlah driver yang harus dialokasikan karena dataset tidak menyediakan seluruh supply-side variables yang diperlukan untuk optimization.

---

## 19. Perbedaan Dashboard dan Forecasting Application

Keduanya memiliki tujuan yang berbeda.

### Dashboard

Menjawab:

> **Apa yang telah terjadi?**

Fokus:

- historical performance;
- demand pattern;
- location performance;
- operational performance;
- financial performance.

### Forecasting Application

Menjawab:

> **Apa yang kemungkinan akan terjadi?**

Fokus:

- predicted future demand;
- expected high-demand zone;
- expected high-demand time;
- expected uplift terhadap typical demand.

Dengan demikian project memiliki dua sisi:

```text
NYC TLC HVFHV MONTHLY PARQUET
Jan 2024 – May 2026
29 monthly files
        │
        ▼
JANUARY 2024 PILOT
Data Understanding
Data Quality Assessment
Cleaning Decision
        │
        ▼
CLEANING & VALIDATION RULES
        │
        ▼
PYTHON + DUCKDB PIPELINE
Process one month at a time
        │
        ├── Monthly Data Quality Monitoring
        │
        ├── Apply Cleaning Rules
        │
        ├── Standardize Variables
        │
        └── Transformation / Aggregation
        │
        ▼
LOCAL STAGING OUTPUT
        │
        ├── Business Analytics Staging Data
        ├── Hourly Demand Staging Data
        └── Monthly Data Quality Report
        │
        ▼
BIGQUERY SANDBOX
Dataset: ride_hailing
        │
        ▼
BIGQUERY SQL TRANSFORMATION
        │
        ├── Business Analytical Mart
        ├── Forecast Feature Mart
        └── Forecast Result Mart
        │
        ├─────────────────────┐
        ▼                     ▼
 BUSINESS ANALYTICS       FORECASTING
        │                     │
        ▼                     ▼
    DASHBOARD              PYTHON MODEL
                              │
                              ▼
                        MODEL EVALUATION
                              │
                              ▼
                        FORECAST RESULTS
                              │
                              ▼
                           STREAMLIT
```

---

## 20. Deliverables Project

Project final direncanakan menghasilkan:

### 1. Data Pipeline
DuckDB + SQL + BigQuery Sandbox untuk data quality, cleaning, transformation, aggregation, dan analytical marts.

### 2. Business Dashboard
Dashboard historical ride-hailing analytics.

### 3. Forecasting Notebook
EDA time-series, baseline, statistical models, ML models, validation, tuning, dan final evaluation.

### 4. Forecasting Deployment
Streamlit application untuk menampilkan future demand prediction.

### 5. Project Documentation
Dokumentasi business problem, data understanding, methodology, findings, limitations, dan business recommendations.

---

## 21. Status Project Saat Ini

Tahap yang telah dilakukan:

- BigQuery Sandbox telah disiapkan.
- Dataset `ride_hailing` telah dibuat.
- Raw HVFHV Januari 2024 telah berhasil dibaca menggunakan DuckDB di VS Code.
- Schema 24 kolom telah berhasil diperiksa.
- Provider distribution telah diperiksa.
- Missing `request_datetime` telah diperiksa.
- Missing dan invalid `PULocationID` telah diperiksa.

Project saat ini berada pada tahap:

> **Data Understanding dan Preliminary Data Quality Assessment**

Belum dilakukan final cleaning, filtering provider, aggregation, feature engineering, maupun modeling.

Hal tersebut disengaja agar setiap cleaning decision memiliki dasar yang jelas dari kondisi aktual data.

---

## 22. Tahapan Berikutnya

Urutan pekerjaan selanjutnya adalah:

1. Menyelesaikan data quality assessment Januari 2024.
2. Memeriksa duplicate, temporal consistency, dan numerical anomalies.
3. Menentukan cleaning rules berdasarkan hasil pemeriksaan.
4. Menentukan provider scope untuk dashboard dan forecasting.
5. Menguji transformation pada Januari 2024.
6. Menerapkan pipeline yang sama ke seluruh Jan 2024–Mei 2026.
7. Membentuk business analytical marts.
8. Memuat hasil agregasi ke BigQuery Sandbox.
9. Melakukan historical EDA dan membangun dashboard.
10. Membentuk hourly demand time series.
11. Melakukan forecasting feature engineering.
12. Melakukan baseline dan model screening.
13. Melakukan walk-forward validation dan hyperparameter tuning.
14. Melakukan final test pada Jan–Mei 2026.
15. Membuat business interpretation dari forecast.
16. Melakukan deployment menggunakan Streamlit.

---

## 23. Batasan Project

Beberapa batasan perlu dinyatakan sejak awal:

1. Dataset berisi aktivitas perjalanan, bukan keseluruhan informasi supply driver.
2. Forecasting demand tidak sama dengan driver allocation optimization.
3. Driver availability, online driver count, acceptance rate, utilization, repositioning cost, dan beberapa supply-side constraints tidak tersedia lengkap.
4. BigQuery Sandbox memiliki keterbatasan storage sehingga raw trip-level data tidak dimasukkan seluruhnya ke warehouse.
5. Forecast accuracy dapat berubah pada unusual events yang tidak direpresentasikan oleh historical features.
6. External information seperti weather atau event schedule dapat ditambahkan pada pengembangan berikutnya apabila tersedia dan diketahui pada forecast time.

---

## 24. Ringkasan Project

Project **Ride-Hailing Demand and Operational Analytics with Demand Forecasting** dirancang sebagai end-to-end data project yang menggabungkan data processing, SQL, data warehouse, business analytics, forecasting, dashboard, dan deployment.

Raw HVFHV trip records periode Januari 2024–Mei 2026 diproses menggunakan DuckDB. Januari 2024 digunakan terlebih dahulu sebagai pilot untuk memahami data dan memvalidasi pipeline. Setelah aturan data quality dan transformation dinyatakan benar, proses diterapkan pada seluruh 29 bulan.

Historical analytical marts digunakan untuk menjelaskan performa bisnis dan operasional melalui dashboard. Secara terpisah, trip-level records ditransformasikan menjadi hourly pickup-zone demand untuk kebutuhan forecasting.

Model dikembangkan menggunakan chronological validation sehingga future test data tidak digunakan pada proses pemilihan model. Output forecasting kemudian diterjemahkan menjadi expected high-demand zone/time dan disajikan melalui Streamlit sebagai early signal untuk driver supply planning.

Dengan desain tersebut, project tidak hanya menunjukkan kemampuan membuat prediction model, tetapi juga memperlihatkan pemahaman terhadap keseluruhan data lifecycle mulai dari raw data, data quality, ETL, SQL, analytical warehouse, business insight, forecasting, hingga deployment.
