"""
main.py - API Python (FastAPI) untuk FCM + KNN prediksi churn.

Laravel hanya mengurus tampilan dan database; seluruh perhitungan fuzzy dilakukan di sini.

Jalankan:  uvicorn main:app --host 127.0.0.1 --port 8001
Dokumentasi interaktif otomatis: http://127.0.0.1:8001/docs
"""
import io
import re
import uuid
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from modules import evaluation as ev
from modules.pipeline import ChurnFuzzyPipeline, Params
from modules.preprocessing import (BINARY_COLS, CATEGORICAL_COLS, NUMERIC_COLS,
                                   DataValidationError, validate_dataframe)

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_cache: Dict[str, ChurnFuzzyPipeline] = {}

app = FastAPI(title="API FCM + KNN Prediksi Churn", version="1.0")


# ----------------------------------------------------------------------------- util
def clean(obj):
    """Ubah tipe NumPy menjadi tipe Python biasa agar bisa dijadikan JSON."""
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return clean(obj.tolist())
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return None if np.isnan(obj) else float(obj)
    return obj


def read_csv_upload(file: UploadFile) -> pd.DataFrame:
    raw = file.file.read()
    try:
        return pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(422, f"File tidak dapat dibaca sebagai CSV: {e}")


def check_model_id(model_id: str):
    if not MODEL_ID_RE.match(model_id or ""):
        raise HTTPException(422, "model_id tidak valid.")


def load_model(model_id: str) -> ChurnFuzzyPipeline:
    check_model_id(model_id)
    if model_id in _cache:
        return _cache[model_id]
    path = MODEL_DIR / f"{model_id}.joblib"
    if not path.exists():
        raise HTTPException(404, "Model tidak ditemukan di API Python. Jalankan ulang proses (menu Proses).")
    pipe = ChurnFuzzyPipeline()
    pipe.results = joblib.load(path)
    _cache[model_id] = pipe
    return pipe


def metrics_out(m):
    return {"accuracy": m["accuracy"], "precision": m["precision"], "recall": m["recall"],
            "f1": m["f1"], "confusion_matrix": m["confusion_matrix"].tolist()}


# ----------------------------------------------------------------------------- endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/inspect")
def inspect(file: UploadFile = File(...)):
    """Validasi dataset dan kembalikan ringkasan + pratinjau 50 baris."""
    df = read_csv_upload(file)
    try:
        validate_dataframe(df)
    except DataValidationError as e:
        raise HTTPException(422, str(e))
    churn_rate = float((df["Churn"].astype(str).str.strip() == "Yes").mean())
    return {"n_rows": int(len(df)), "n_cols": int(df.shape[1]), "churn_rate": churn_rate,
            "columns": list(df.columns),
            "preview": df.head(50).fillna("").astype(str).values.tolist()}


@app.post("/train")
def train(file: UploadFile = File(...),
          n_clusters: int = Form(3), m: float = Form(2.0), tol: float = Form(1e-5),
          max_iter: int = Form(300), k: int = Form(5), test_size: float = Form(0.2),
          membership_weight: float = Form(1.0), random_state: int = Form(42)):
    df = read_csv_upload(file)
    params = Params(n_clusters=n_clusters, m=m, tol=tol, max_iter=max_iter, k=k,
                    test_size=test_size, membership_weight=membership_weight,
                    random_state=random_state)
    logs = []
    pipe = ChurnFuzzyPipeline()
    try:
        r = pipe.run(df, params, log=logs.append)
    except (DataValidationError, ValueError) as e:
        raise HTTPException(422, str(e))

    model_id = uuid.uuid4().hex
    joblib.dump({key: r[key] for key in ("prep", "fcm", "knn_base", "knn_comb", "profile")},
                MODEL_DIR / f"{model_id}.joblib")

    df_tr, labels = r["df_train"], r["labels_train"]
    idx = np.random.default_rng(0).choice(len(df_tr), min(len(df_tr), 1500), replace=False)
    scatter = [[round(float(df_tr["tenure"].iat[i]), 2), round(float(df_tr["MonthlyCharges"].iat[i]), 2),
                int(labels[i])] for i in idx]
    test_rows = []
    for i in range(min(300, len(r["U_test"]))):
        u = r["U_test"][i]
        test_rows.append({"mu": [round(float(x), 4) for x in u], "cluster": int(np.argmax(u)) + 1,
                          "actual": int(r["y_test"][i]), "pred": int(r["pred_comb"][i])})
    v = r["validity"]
    return clean({
        "model_id": model_id,
        "logs": logs,
        "clean_report": r["clean_report"],
        "params": params.__dict__,
        "metrics_base": metrics_out(r["metrics_base"]),
        "metrics_comb": metrics_out(r["metrics_comb"]),
        "validity": {"silhouette": v["silhouette"], "pc": v["pc"], "pe": v["pe"], "J": v["J"],
                     "iterations": v["iterations"], "converged": v["converged"]},
        "profile": r["profile"],
        "overall": r["overall"],
        "centers": r["centers_orig"],
        "history": [list(h) for h in r["fcm"].history_],
        "scatter": scatter,
        "test_rows": test_rows,
        "text_clusters": r["text_clusters"],
        "text_comparison": r["text_comparison"],
        "limitations": ev.LIMITATIONS,
        "n_train": int(len(r["df_train"])), "n_test": int(len(r["df_test"])),
    })


class PredictRequest(BaseModel):
    model_id: str
    values: Dict[str, Any]


@app.post("/predict")
def predict(req: PredictRequest):
    pipe = load_model(req.model_id)
    prep = pipe.results["prep"]
    allowed = set(NUMERIC_COLS + BINARY_COLS + CATEGORICAL_COLS)
    values = {}
    for key, raw in req.values.items():
        if key not in allowed:
            raise HTTPException(422, f"Kolom tidak dikenal: {key}")
        if key in NUMERIC_COLS + BINARY_COLS:
            try:
                num = float(raw)
            except (TypeError, ValueError):
                raise HTTPException(422, f"Nilai '{key}' harus berupa angka.")
            if num < 0:
                raise HTTPException(422, f"Nilai '{key}' tidak boleh negatif.")
            values[key] = int(num) if key in BINARY_COLS else num
        else:
            if raw not in prep.levels[key]:
                raise HTTPException(422, f"Nilai '{raw}' tidak dikenal untuk '{key}'. "
                                         f"Pilihan: {', '.join(map(str, prep.levels[key]))}")
            values[key] = raw
    out = pipe.predict_one(values)
    prof = next((p for p in pipe.results["profile"] if p["cluster"] == out["cluster"]), None)
    return clean({**out, "cluster_churn_rate": prof["churn"] if prof else None})


@app.delete("/models/{model_id}")
def delete_model(model_id: str):
    check_model_id(model_id)
    _cache.pop(model_id, None)
    path = MODEL_DIR / f"{model_id}.joblib"
    if path.exists():
        path.unlink()
    return {"deleted": True}
