"""
run_experiments.py - Menjalankan skenario pengujian S1-S5 (Bab III, Tabel 3.6)
pada dataset Telco asli memakai ChurnFuzzyPipeline milik proyek.

Cara pakai:
  1. Letakkan file ini di folder yang sama dengan app.py.
  2. Pastikan data/WA_Fn-UseC_-Telco-Customer-Churn.csv ada.
  3. Jalankan:  python run_experiments.py

Hasil disimpan di folder hasil_pengujian/ (CSV, dapat dibuka di Excel).
Satu parameter diubah dalam satu waktu; parameter lain mengikuti nilai bawaan Params().
"""
import json
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from modules.pipeline import ChurnFuzzyPipeline, Params

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUT = ROOT / "hasil_pengujian"
OUT.mkdir(exist_ok=True)

FIELDS = ["n_clusters", "m", "tol", "max_iter", "k",
          "test_size", "membership_weight", "random_state"]
SCENARIOS = {
    "S1": ("n_clusters", "Jumlah cluster c", [2, 3, 4, 5, 6]),
    "S2": ("m", "Fuzzifier m", [1.5, 2.0, 2.5, 3.0]),
    "S3": ("k", "Tetangga k", [3, 5, 7, 11, 15, 21]),
    "S4": ("membership_weight", "Bobot membership w", [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]),
}

df = pd.read_csv(DATA)
BASE = Params()


def make(**kw):
    values = {f: getattr(BASE, f) for f in FIELDS}
    values.update(kw)
    return Params(**values)


def run(params):
    return ChurnFuzzyPipeline().run(df, params, log=lambda s: None)


def rows_from(scn, label, value, r):
    b, g, v = r["metrics_base"], r["metrics_comb"], r["validity"]
    out = []
    for name, mt in (("Baseline", b), ("FCM + KNN", g)):
        is_fcm = name == "FCM + KNN"
        out.append({
            "Skenario": scn, "Variabel": label, "Nilai": value, "Model": name,
            "Akurasi": round(mt["accuracy"], 4), "Precision": round(mt["precision"], 4),
            "Recall": round(mt["recall"], 4), "F1": round(mt["f1"], 4),
            "Silhouette": (None if v["silhouette"] is None else round(v["silhouette"], 4)) if is_fcm else None,
            "PC": round(v["pc"], 4) if is_fcm else None,
            "PE": round(v["pe"], 4) if is_fcm else None,
            "J_akhir": round(v["J"], 2) if is_fcm else None,
            "Iterasi": v["iterations"] if is_fcm else None,
            "Konvergen": ("Ya" if v["converged"] else "Tidak") if is_fcm else None,
        })
    return out


# ------------------------------------------------------------ info dataset
raw_churn = (df["Churn"].astype(str).str.strip() == "Yes").mean() * 100
blank_total = int(pd.to_numeric(df["TotalCharges"], errors="coerce").isna().sum())
info = {
    "baris": len(df), "kolom": df.shape[1],
    "tingkat_churn_persen": round(raw_churn, 2),
    "totalcharges_kosong": blank_total,
    "parameter_bawaan": {f: getattr(BASE, f) for f in FIELDS},
}

# ------------------------------------------------------------ konfigurasi dasar
all_rows, details = [], {}
print("Menjalankan konfigurasi dasar ...")
r0 = run(make())
all_rows += rows_from("Dasar", "Parameter bawaan", "-", r0)
try:
    info["jumlah_fitur_knn_baseline"] = len(r0["prep"].feature_names)
except Exception:
    pass
details["dasar"] = {
    "confusion_matrix_fcm_knn": np.asarray(r0["metrics_comb"]["confusion_matrix"]).tolist(),
    "confusion_matrix_baseline": np.asarray(r0["metrics_base"]["confusion_matrix"]).tolist(),
    "profil_segmen": [{k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                       for k, v in q.items()} for q in r0["profile"]],
    "pusat_cluster_satuan_asli": np.round(r0["centers_orig"], 3).tolist(),
}

# ------------------------------------------------------------ skenario S1-S4
best = {}
for scn, (field, label, values) in SCENARIOS.items():
    scn_rows = []
    for val in values:
        print(f"{scn}: {label} = {val}")
        try:
            r = run(make(**{field: val}))
        except Exception:
            print("  GAGAL:")
            traceback.print_exc()
            continue
        scn_rows += rows_from(scn, label, val, r)
        if scn == "S4" and val == 0:
            gap = abs(r["metrics_comb"]["f1"] - r["metrics_base"]["f1"])
            print("  Uji kewajaran w=0 (F1 gabungan harus sama dengan baseline):",
                  "OK" if gap < 1e-9 else f"TIDAK SAMA (selisih {gap:.6f}), periksa implementasi")
    all_rows += scn_rows
    if scn_rows:
        fcm_rows = [x for x in scn_rows if x["Model"] == "FCM + KNN"]
        best[field] = max(fcm_rows, key=lambda x: x["F1"])["Nilai"]
    pd.DataFrame(scn_rows).to_csv(OUT / f"{scn}.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------ S5: konfigurasi akhir
print("S5: konfigurasi akhir dengan parameter terbaik:", best)
r5 = run(make(**best))
all_rows += rows_from("S5", "Konfigurasi akhir", json.dumps(best), r5)
details["S5"] = {
    "parameter": best,
    "confusion_matrix_fcm_knn": np.asarray(r5["metrics_comb"]["confusion_matrix"]).tolist(),
    "confusion_matrix_baseline": np.asarray(r5["metrics_base"]["confusion_matrix"]).tolist(),
    "profil_segmen": [{k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                       for k, v in q.items()} for q in r5["profile"]],
    "pusat_cluster_satuan_asli": np.round(r5["centers_orig"], 3).tolist(),
}

pd.DataFrame(all_rows).to_csv(OUT / "semua_hasil.csv", index=False, encoding="utf-8-sig")
(OUT / "info_dataset.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "detail_dasar_dan_S5.json").write_text(
    json.dumps(details, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

print("\nSelesai. Berkas ada di folder:", OUT)
print("Kirim isi semua_hasil.csv, info_dataset.json, dan detail_dasar_dan_S5.json ke Claude.")
