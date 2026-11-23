# Segmentasi & Prediksi Churn Pelanggan Telco: Fuzzy C-Means + KNN (Streamlit)

Final Project Teknologi Logika Fuzzy. Aplikasi web Python murni dengan Streamlit.

```
Data -> Preprocessing -> FCM -> Derajat keanggotaan (mu) -> KNN [fitur asli + mu] -> Prediksi + Evaluasi
```

## Menjalankan di laptop

Windows (CMD):
```
cd churn_streamlit
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```
PowerShell: ganti baris aktivasi dengan `.\venv\Scripts\Activate.ps1`
(jika ditolak: `Set-ExecutionPolicy -Scope Process Bypass`, atau pakai CMD).

Browser akan terbuka di http://localhost:8501.

## Dataset
- Letakkan file asli **Telco Customer Churn** di `data/WA_Fn-UseC_-Telco-Customer-Churn.csv`
  (cari "Telco Customer Churn" di Kaggle). Jika file itu ada di repo, menu **Input Data** menyediakan
  pilihan "Dataset bawaan repo" sehingga versi online tidak perlu upload.
- Atau unggah CSV langsung lewat menu **Input Data**.
- Pilihan "Data contoh sintetis" hanya untuk uji coba. **Jangan dipakai untuk laporan.**

## Deploy ke Streamlit Community Cloud (gratis)

1. **Upload ke GitHub** (aplikasi harus ada di root repo: `app.py`, `requirements.txt`, `modules/`):
   ```
   git init
   git add .
   git status
   git commit -m "Versi awal Streamlit"
   git branch -M main
   git remote add origin https://github.com/USERNAMEMU/NAMAREPO.git
   git push -u origin main
   ```
   Repo boleh **private**.
2. Buka https://share.streamlit.io dan login dengan GitHub.
3. Klik **Create app** -> **Deploy a public app from GitHub** (atau pilih repo private; izinkan akses jika diminta).
4. Isi: **Repository** = repo kamu, **Branch** = `main`, **Main file path** = `app.py`.
5. Buka **Advanced settings**, pilih **Python 3.12**, lalu klik **Deploy**.
6. Tunggu build 2-5 menit. Alamat aplikasi: `https://namaapp.streamlit.app`. Setiap `git push` memperbarui aplikasi otomatis.

Catatan versi online:
- Aplikasi gratis akan "tidur" jika lama tidak dibuka; klik tombol bangunkan, butuh sekitar setengah menit.
- Riwayat prediksi tersimpan selama sesi browser. Jika halaman dimuat ulang, riwayat hilang (ada tombol unduh CSV).
- Hasil proses disimpan di memori sesi, bukan di database.
- Sebelum presentasi, buka link dan jalankan satu proses agar tidak kaget dengan waktu bangun.

## Struktur
```
app.py                    aplikasi Streamlit (7 menu)
modules/fcm.py            Fuzzy C-Means (NumPy, implementasi mandiri)
modules/preprocessing.py  validasi, pembersihan, one-hot, standarisasi
modules/classifier.py     KNN dengan fitur [fitur asli | bobot x membership]
modules/evaluation.py     metrik, validitas cluster, teks interpretasi
modules/pipeline.py       alur end-to-end dan prediksi satu pelanggan
data/                     dataset (taruh CSV asli di sini) + pembuat data sintetis
tests/test_app.py         uji end-to-end antarmuka tanpa browser
.streamlit/config.toml    tema warna
```

Uji otomatis: `python tests/test_app.py`.

## Parameter
| Parameter | Default | Keterangan |
|---|---|---|
| c | 3 | jumlah cluster (2-10) |
| m | 2.0 | fuzzifier (>1) |
| epsilon | 1e-5 | batas konvergensi perubahan U |
| iterasi maks | 300 | |
| k | 5 | tetangga KNN |
| data uji | 0.2 | proporsi |
| bobot membership | 1.0 | pengali kolom membership di KNN |
| random state | 42 | |

## Masalah umum
| Gejala | Solusi |
|---|---|
| `streamlit` tidak dikenali | Aktifkan venv, atau jalankan `python -m streamlit run app.py` |
| `No module named 'modules'` | Jalankan dari folder yang berisi `app.py` |
| Build gagal di Cloud (`ModuleNotFoundError`) | Pastikan `requirements.txt` ada di root repo dan sudah di-push |
| Dataset ditolak | Pesan di aplikasi menyebut kolom yang kurang; pakai file Telco asli |
