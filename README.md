# FCM + KNN Prediksi Churn Pelanggan

Aplikasi Streamlit untuk melakukan segmentasi pelanggan telekomunikasi menggunakan **Fuzzy C-Means (FCM)** dan memprediksi **churn** menggunakan **K-Nearest Neighbor (KNN)**.

## Fitur

- Memuat data melalui unggahan CSV, tabel manual, atau data bawaan.
- Melakukan segmentasi pelanggan dengan Fuzzy C-Means.
- Menambahkan derajat keanggotaan FCM sebagai fitur prediksi.
- Membandingkan KNN baseline dengan KNN berbasis membership FCM.
- Menampilkan metrik evaluasi, visualisasi hasil, dan prediksi pelanggan baru.
- Menyediakan tampilan informasi tentang metode, parameter, dan rumus.

## Teknologi

- Python 3.12
- Streamlit
- NumPy
- pandas
- scikit-learn
- Plotly

## Persyaratan

- Python 3.12 atau versi yang kompatibel
- pip
- Sistem operasi Windows, Linux, atau macOS

## Instalasi

Masuk ke folder proyek:

```powershell
cd "fcm-knn-churn-kelompok5"
```

Buat dan aktifkan environment virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependency:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```powershell
streamlit run app.py
```

Streamlit akan menampilkan alamat lokal, biasanya `http://localhost:8501`.

## Penggunaan

1. Buka menu **Input Data**.
2. Pilih salah satu sumber data:
   - Unggah file CSV.
   - Isi data melalui tabel manual.
   - Gunakan **Data Bawaan** untuk data contoh.
   - Gunakan dataset bawaan repo jika file dataset tersedia.
3. Buka menu **Proses**.
4. Atur parameter FCM dan KNN, lalu jalankan proses.
5. Lihat hasil segmentasi pada menu **Hasil**.
6. Bandingkan performa model pada menu **Evaluasi**.
7. Prediksi satu pelanggan baru pada menu **Prediksi**.

## Format Dataset

Dataset CSV harus memiliki kolom berikut:

- `customerID`
- `gender`
- `SeniorCitizen`
- `Partner`
- `Dependents`
- `tenure`
- `PhoneService`
- `MultipleLines`
- `InternetService`
- `OnlineSecurity`
- `OnlineBackup`
- `DeviceProtection`
- `TechSupport`
- `StreamingTV`
- `StreamingMovies`
- `Contract`
- `PaperlessBilling`
- `PaymentMethod`
- `MonthlyCharges`
- `TotalCharges`
- `Churn`

Nilai `Churn` menggunakan `Yes` atau `No`. Saat input manual, minimal 50 baris data dengan kedua label tersebut direkomendasikan agar proses evaluasi berjalan baik.

## Struktur Folder

```text
fcm-knn-churn-kelompok5/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── generate_sample_telco.py
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── modules/
│   ├── preprocessing.py
│   ├── fcm.py
│   ├── classifier.py
│   ├── evaluation.py
│   └── pipeline.py
└── tests/
    └── test_app.py
```

## Pengujian

Jalankan pengujian antarmuka Streamlit dari folder proyek:

```powershell
python tests/test_app.py
```

## Metode

### Fuzzy C-Means

FCM mengelompokkan pelanggan ke beberapa cluster tanpa batas keanggotaan yang kaku. Setiap pelanggan memiliki derajat keanggotaan pada setiap cluster. Nilai parameter yang dapat diatur meliputi:

- Jumlah cluster `c`
- Nilai fuzziness `m`
- Nilai epsilon konvergensi
- Batas iterasi maksimum

### K-Nearest Neighbor

KNN memprediksi status churn pelanggan baru berdasarkan tetangga terdekat pada ruang fitur. Aplikasi membandingkan:

- KNN baseline menggunakan fitur hasil preprocessing.
- KNN gabungan menggunakan fitur preprocessing dan membership FCM.

## Lisensi

Proyek ini dibuat untuk keperluan pembelajaran dan tugas akademik.
