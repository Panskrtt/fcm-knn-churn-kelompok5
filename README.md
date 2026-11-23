# Segmentasi dan Prediksi Churn Telco

Aplikasi Streamlit untuk segmentasi pelanggan dengan Fuzzy C-Means (FCM) dan prediksi churn dengan KNN.

## Jalankan

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501`.

## Uji

```powershell
python tests/test_app.py
```

## Struktur

- `app.py`: antarmuka Streamlit
- `modules/`: preprocessing, FCM, KNN, evaluasi, dan pipeline
- `data/`: generator data sintetis
- `tests/`: uji aplikasi
- `.streamlit/config.toml`: konfigurasi tema
