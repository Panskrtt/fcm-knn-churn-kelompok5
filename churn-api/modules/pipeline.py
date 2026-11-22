"""
pipeline.py - Orkestrasi alur lengkap FCM -> KNN.

Tahapan run():
  1. Validasi & pembersihan data
  2. Pembagian data latih/uji (stratified)
  3. Encoding + standarisasi (fit pada data latih)
  4. Fuzzy C-Means pada fitur numerik data latih
  5. Derajat keanggotaan data latih & data uji terhadap pusat cluster
  6. KNN baseline (tanpa membership) dan KNN gabungan (fitur asli + membership)
  7. Evaluasi
"""
from dataclasses import dataclass

import numpy as np
from sklearn.model_selection import train_test_split

from . import evaluation as ev
from .classifier import MembershipKNN
from .fcm import FuzzyCMeans
from .preprocessing import (NUMERIC_COLS, TARGET_COL, Preprocessor, clean_data,
                            validate_dataframe)


@dataclass
class Params:
    n_clusters: int = 3
    m: float = 2.0
    tol: float = 1e-5
    max_iter: int = 300
    k: int = 5
    test_size: float = 0.2
    membership_weight: float = 1.0
    random_state: int = 42

    def validate(self):
        if not 2 <= self.n_clusters <= 10:
            raise ValueError("Jumlah cluster harus antara 2 dan 10.")
        if not 1.0 < self.m <= 5.0:
            raise ValueError("Fuzzifier m harus > 1 dan <= 5.")
        if not 0 < self.tol < 1:
            raise ValueError("Toleransi konvergensi harus di antara 0 dan 1 (contoh 1e-5).")
        if not 1 <= self.max_iter <= 1000:
            raise ValueError("Iterasi maksimum harus antara 1 dan 1000.")
        if not 1 <= self.k <= 50:
            raise ValueError("Nilai k KNN harus antara 1 dan 50.")
        if not 0.1 <= self.test_size <= 0.5:
            raise ValueError("Proporsi data uji harus antara 0.1 dan 0.5.")
        if not 0 <= self.membership_weight <= 10:
            raise ValueError("Bobot fitur membership harus antara 0 dan 10.")


class ChurnFuzzyPipeline:
    def __init__(self):
        self.results = None

    def run(self, df_raw, p, log=print):
        p.validate()
        validate_dataframe(df_raw)

        log("[1/7] Membersihkan data ...")
        df, rep = clean_data(df_raw)
        log(f"      baris awal {rep['baris_awal']}, TotalCharges kosong {rep['totalcharges_kosong']} "
            f"(diisi tenure x MonthlyCharges), baris dibuang {rep['baris_dibuang']}, baris akhir {rep['baris_akhir']}")
        y = (df[TARGET_COL] == "Yes").astype(int).to_numpy()
        if min(np.bincount(y)) < 2:
            raise ValueError("Salah satu kelas churn terlalu sedikit setelah pembersihan data.")

        log("[2/7] Membagi data latih/uji (stratified) ...")
        idx = np.arange(len(df))
        tr, te = train_test_split(idx, test_size=p.test_size, stratify=y, random_state=p.random_state)
        if p.k > len(tr):
            raise ValueError(f"Nilai k ({p.k}) lebih besar dari jumlah data latih ({len(tr)}).")
        df_tr, df_te = df.iloc[tr].reset_index(drop=True), df.iloc[te].reset_index(drop=True)
        y_tr, y_te = y[tr], y[te]
        log(f"      latih {len(tr)} | uji {len(te)} | churn latih {y_tr.mean()*100:.1f}% | churn uji {y_te.mean()*100:.1f}%")

        log("[3/7] One-hot encoding + standarisasi (fit pada data latih) ...")
        prep = Preprocessor().fit(df_tr)
        X_tr, Xc_tr = prep.transform(df_tr)
        X_te, Xc_te = prep.transform(df_te)
        log(f"      jumlah fitur KNN (sebelum ditambah membership): {X_tr.shape[1]}; fitur FCM: {Xc_tr.shape[1]} {NUMERIC_COLS}")

        log(f"[4/7] Fuzzy C-Means (c={p.n_clusters}, m={p.m}, eps={p.tol}, iterasi maks={p.max_iter}) ...")
        fcm = FuzzyCMeans(p.n_clusters, p.m, p.max_iter, p.tol, p.random_state).fit(Xc_tr)
        it, J, delta = fcm.history_[-1]
        status = "konvergen" if delta < p.tol else "mencapai iterasi maksimum (belum konvergen)"
        log(f"      berhenti pada iterasi {it}: J = {J:.4f}, delta U = {delta:.2e} -> {status}")

        log("[5/7] Menghitung derajat keanggotaan data latih dan data uji ...")
        U_tr = fcm.predict_membership(Xc_tr)
        U_te = fcm.predict_membership(Xc_te)
        labels_tr = np.argmax(U_tr, axis=1)

        log(f"[6/7] Melatih KNN (k={p.k}): baseline vs gabungan (bobot membership {p.membership_weight}) ...")
        knn_base = MembershipKNN(p.k, p.membership_weight, use_membership=False).fit(X_tr, U_tr, y_tr)
        knn_comb = MembershipKNN(p.k, p.membership_weight, use_membership=True).fit(X_tr, U_tr, y_tr)
        pred_base = knn_base.predict(X_te, U_te)
        pred_comb = knn_comb.predict(X_te, U_te)
        proba_comb = knn_comb.predict_proba_churn(X_te, U_te)

        log("[7/7] Evaluasi ...")
        m_base = ev.classification_metrics(y_te, pred_base)
        m_comb = ev.classification_metrics(y_te, pred_comb)
        validity = ev.cluster_validity(Xc_tr, labels_tr, U_tr)
        validity["J"] = J
        validity["iterations"] = it
        validity["converged"] = bool(delta < p.tol)
        sil = "n/a" if validity["silhouette"] is None else f"{validity['silhouette']:.3f}"
        log(f"      silhouette {sil} | PC {validity['pc']:.3f} | PE {validity['pe']:.3f}")
        log(f"      F1 churn baseline {m_base['f1']:.3f} | gabungan {m_comb['f1']:.3f}")

        # profil cluster (data latih)
        overall = {"tenure": float(df_tr["tenure"].mean()), "monthly": float(df_tr["MonthlyCharges"].mean()),
                   "total": float(df_tr["TotalCharges"].mean()), "churn": float(y_tr.mean())}
        profile = []
        for j in range(p.n_clusters):
            mask = labels_tr == j
            n = int(mask.sum())
            if n == 0:
                continue
            profile.append({
                "cluster": j + 1, "n": n, "pct": n / len(df_tr) * 100,
                "tenure": float(df_tr.loc[mask, "tenure"].mean()),
                "monthly": float(df_tr.loc[mask, "MonthlyCharges"].mean()),
                "total": float(df_tr.loc[mask, "TotalCharges"].mean()),
                "churn": float(y_tr[mask].mean()),
            })

        self.results = {
            "params": p, "clean_report": rep, "prep": prep, "fcm": fcm,
            "knn_base": knn_base, "knn_comb": knn_comb,
            "df_train": df_tr, "df_test": df_te, "y_train": y_tr, "y_test": y_te,
            "U_train": U_tr, "U_test": U_te, "labels_train": labels_tr,
            "centers_orig": prep.inverse_numeric(fcm.centers_),
            "pred_base": pred_base, "pred_comb": pred_comb, "proba_comb": proba_comb,
            "metrics_base": m_base, "metrics_comb": m_comb, "validity": validity,
            "profile": profile, "overall": overall,
            "text_clusters": ev.describe_clusters(profile, overall),
            "text_comparison": ev.describe_comparison(m_base, m_comb),
        }
        return self.results

    def predict_one(self, values):
        """Prediksi satu pelanggan dari input manual (dict kolom -> nilai)."""
        r = self.results
        if r is None:
            raise RuntimeError("Model belum dilatih.")
        row = r["prep"].row_from_values(values)
        X, Xc = r["prep"].transform(row)
        U = r["fcm"].predict_membership(Xc)
        pred = int(r["knn_comb"].predict(X, U)[0])
        proba = float(r["knn_comb"].predict_proba_churn(X, U)[0])
        pred_base = int(r["knn_base"].predict(X, U)[0])
        return {"membership": U[0], "cluster": int(np.argmax(U[0])) + 1, "pred": pred,
                "proba_churn": proba, "pred_base": pred_base}
