"""
preprocessing.py - Validasi, pembersihan, encoding, dan normalisasi data Telco Customer Churn.

Alur:
  1. validate_dataframe : cek kolom wajib, isi kolom target, jumlah baris.
  2. clean_data         : rapikan teks, ubah kolom numerik, tangani TotalCharges kosong.
  3. Preprocessor       : one-hot encoding + standarisasi (z-score) yang di-fit HANYA pada data latih,
                          lalu dipakai untuk data uji dan data manual (mencegah data leakage).
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
BINARY_COLS = ["SeniorCitizen"]
CATEGORICAL_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]
TARGET_COL = "Churn"
REQUIRED_COLUMNS = NUMERIC_COLS + BINARY_COLS + CATEGORICAL_COLS + [TARGET_COL]
CLUSTER_COLS = NUMERIC_COLS  # fitur yang dipakai FCM (setelah distandarisasi)

COLUMN_DESCRIPTIONS = {
    "customerID": "ID pelanggan (tidak dipakai dalam perhitungan).",
    "gender": "Jenis kelamin pelanggan (Male/Female).",
    "SeniorCitizen": "Apakah pelanggan lansia (1 = ya, 0 = tidak).",
    "Partner": "Memiliki pasangan (Yes/No).",
    "Dependents": "Memiliki tanggungan (Yes/No).",
    "tenure": "Lama berlangganan dalam bulan. [Fitur FCM]",
    "PhoneService": "Berlangganan layanan telepon (Yes/No).",
    "MultipleLines": "Memiliki banyak jalur telepon (Yes/No/No phone service).",
    "InternetService": "Jenis layanan internet (DSL/Fiber optic/No).",
    "OnlineSecurity": "Layanan keamanan online (Yes/No/No internet service).",
    "OnlineBackup": "Layanan backup online (Yes/No/No internet service).",
    "DeviceProtection": "Proteksi perangkat (Yes/No/No internet service).",
    "TechSupport": "Dukungan teknis (Yes/No/No internet service).",
    "StreamingTV": "Layanan streaming TV (Yes/No/No internet service).",
    "StreamingMovies": "Layanan streaming film (Yes/No/No internet service).",
    "Contract": "Jenis kontrak (Month-to-month/One year/Two year).",
    "PaperlessBilling": "Tagihan tanpa kertas (Yes/No).",
    "PaymentMethod": "Metode pembayaran (4 kategori).",
    "MonthlyCharges": "Tagihan bulanan dalam dolar. [Fitur FCM]",
    "TotalCharges": "Total tagihan selama berlangganan dalam dolar. [Fitur FCM]",
    "Churn": "TARGET: pelanggan berhenti berlangganan (Yes/No).",
}


class DataValidationError(Exception):
    """Kesalahan validasi dataset yang pesannya aman ditampilkan ke pengguna."""


def validate_dataframe(df):
    if df is None or df.empty:
        raise DataValidationError("Dataset kosong.")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(
            "Kolom wajib tidak ditemukan: " + ", ".join(missing)
            + ".\nPastikan file adalah dataset Telco Customer Churn."
        )
    if len(df) < 50:
        raise DataValidationError(f"Jumlah baris terlalu sedikit ({len(df)}). Minimal 50 baris.")
    vals = set(df[TARGET_COL].dropna().astype(str).str.strip().unique())
    if not vals.issubset({"Yes", "No"}):
        raise DataValidationError("Kolom Churn hanya boleh berisi 'Yes' atau 'No'. Ditemukan: "
                                  + ", ".join(sorted(vals)))
    if len(vals) < 2:
        raise DataValidationError("Kolom Churn hanya memiliki satu kelas. Klasifikasi membutuhkan dua kelas.")


def clean_data(df):
    """Mengembalikan (df_bersih, laporan)."""
    d = df.copy()
    report = {"baris_awal": len(d)}
    for col in d.columns:
        if d[col].dtype == object:
            d[col] = d[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
    for col in NUMERIC_COLS + BINARY_COLS:
        d[col] = pd.to_numeric(d[col], errors="coerce")  # string kosong -> NaN
    report["totalcharges_kosong"] = int(d["TotalCharges"].isna().sum())
    # TotalCharges kosong (umumnya tenure = 0) diestimasi = tenure * MonthlyCharges
    d["TotalCharges"] = d["TotalCharges"].fillna(d["tenure"] * d["MonthlyCharges"])
    needed = NUMERIC_COLS + BINARY_COLS + CATEGORICAL_COLS + [TARGET_COL]
    d = d.dropna(subset=needed)
    invalid = (d["tenure"] < 0) | (d["MonthlyCharges"] < 0) | (d["TotalCharges"] < 0)
    d = d[~invalid].reset_index(drop=True)
    d["SeniorCitizen"] = d["SeniorCitizen"].astype(int)
    report["baris_akhir"] = len(d)
    report["baris_dibuang"] = report["baris_awal"] - report["baris_akhir"]
    return d, report


class Preprocessor:
    """One-hot encoding + z-score. fit() hanya pada data latih."""

    def fit(self, df):
        self.levels = {c: sorted(df[c].unique().tolist()) for c in CATEGORICAL_COLS}
        self.defaults = {c: df[c].mode().iloc[0] for c in CATEGORICAL_COLS}
        self.defaults.update({c: float(df[c].median()) for c in NUMERIC_COLS})
        self.defaults["SeniorCitizen"] = int(df["SeniorCitizen"].mode().iloc[0])
        self.scaler = StandardScaler().fit(df[NUMERIC_COLS].to_numpy(float))
        self.feature_names = NUMERIC_COLS + BINARY_COLS + [
            f"{c}={lv}" for c in CATEGORICAL_COLS for lv in self.levels[c]
        ]
        return self

    def transform(self, df):
        """Mengembalikan (X_semua_fitur, X_untuk_FCM)."""
        num = self.scaler.transform(df[NUMERIC_COLS].to_numpy(float))
        binary = df[BINARY_COLS].to_numpy(float)
        cats = [
            (df[c].to_numpy()[:, None] == np.array(self.levels[c])[None, :]).astype(float)
            for c in CATEGORICAL_COLS
        ]
        return np.hstack([num, binary] + cats), num

    def inverse_numeric(self, num_scaled):
        """Kembalikan nilai terstandarisasi ke satuan asli (untuk pusat cluster)."""
        return self.scaler.inverse_transform(num_scaled)

    def row_from_values(self, values):
        """Bentuk 1 baris data dari input manual; kolom lain diisi nilai default (modus/median data latih)."""
        merged = dict(self.defaults)
        merged.update(values)
        return pd.DataFrame([merged])
