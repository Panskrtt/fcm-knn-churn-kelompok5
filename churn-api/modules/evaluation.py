"""evaluation.py - Metrik evaluasi klasifikasi & cluster, serta pembuatan teks interpretasi."""
import numpy as np
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             precision_recall_fscore_support, silhouette_score)


def classification_metrics(y_true, y_pred):
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(p), "recall": float(r), "f1": float(f),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]),
    }


def cluster_validity(X, labels, U, max_samples=3000, seed=42):
    """Silhouette (label tegas), Partition Coefficient, Partition Entropy."""
    sil = None
    if len(np.unique(labels)) >= 2:
        sil = float(silhouette_score(
            X, labels, sample_size=min(len(X), max_samples), random_state=seed))
    pc = float(np.mean(np.sum(U ** 2, axis=1)))
    Uc = np.fmax(U, 1e-12)
    pe = float(-np.mean(np.sum(Uc * np.log(Uc), axis=1)))
    return {"silhouette": sil, "pc": pc, "pe": pe}


def _rel(v, ref, tol=0.10):
    if v > ref * (1 + tol):
        return "di atas"
    if v < ref * (1 - tol):
        return "di bawah"
    return "mendekati"


def describe_clusters(profile, overall):
    """profile: list of dict (cluster, n, pct, tenure, monthly, total, churn). overall: dict yang sama."""
    lines = []
    for r in profile:
        lines.append(
            f"Cluster {r['cluster']}: {r['n']} pelanggan ({r['pct']:.1f}%). "
            f"Lama berlangganan rata-rata {r['tenure']:.1f} bulan ({_rel(r['tenure'], overall['tenure'])} "
            f"rata-rata keseluruhan {overall['tenure']:.1f}), tagihan bulanan ${r['monthly']:.2f} "
            f"({_rel(r['monthly'], overall['monthly'])} rata-rata ${overall['monthly']:.2f}), "
            f"tingkat churn {r['churn']*100:.1f}% ({_rel(r['churn'], overall['churn'])} "
            f"rata-rata {overall['churn']*100:.1f}%)."
        )
    top = max(profile, key=lambda r: r["churn"])
    low = min(profile, key=lambda r: r["churn"])
    lines.append("")
    lines.append(
        f"Cluster dengan churn tertinggi adalah Cluster {top['cluster']} ({top['churn']*100:.1f}%), "
        f"sedangkan terendah Cluster {low['cluster']} ({low['churn']*100:.1f}%). "
        "Segmen dengan churn tertinggi dapat menjadi prioritas program retensi."
    )
    lines.append("Catatan: profil dihitung dari data latih dengan label cluster = keanggotaan tertinggi. "
                 "Pelanggan pada kenyataannya dapat menjadi anggota beberapa cluster sekaligus "
                 "(lihat tab Membership).")
    return "\n".join(lines)


def describe_comparison(base, comb):
    d_acc = comb["accuracy"] - base["accuracy"]
    d_f1 = comb["f1"] - base["f1"]
    d_rec = comb["recall"] - base["recall"]
    head = (f"Selisih (gabungan - baseline): akurasi {d_acc*100:+.2f} poin, "
            f"recall churn {d_rec*100:+.2f} poin, F1 {d_f1*100:+.2f} poin.")
    if d_f1 > 0.005:
        verdict = ("Penambahan fitur membership FCM meningkatkan F1 untuk kelas churn, "
                   "sehingga integrasi fuzzy memberi nilai tambah pada konfigurasi ini.")
    elif d_f1 < -0.005:
        verdict = ("Penambahan fitur membership FCM tidak meningkatkan F1 (justru turun). "
                   "Pada konfigurasi ini fitur membership belum memberi informasi tambahan. "
                   "Coba ubah jumlah cluster, fuzzifier m, nilai k, atau bobot membership.")
    else:
        verdict = ("Performa gabungan relatif sama dengan baseline. Manfaat FCM pada konfigurasi ini "
                   "lebih berupa segmentasi yang dapat diinterpretasi daripada peningkatan akurasi.")
    return head + "\n" + verdict


LIMITATIONS = (
    "Keterbatasan sistem:\n"
    "- Kelas churn tidak seimbang (churn jauh lebih sedikit), sehingga akurasi saja dapat menyesatkan; "
    "perhatikan precision, recall, dan F1 kelas churn.\n"
    "- FCM hanya memakai tiga fitur numerik (tenure, MonthlyCharges, TotalCharges), "
    "sehingga segmentasi belum mencerminkan fitur kategorikal.\n"
    "- FCM bergantung inisialisasi acak dan dapat berhenti di optimum lokal; ubah random state untuk mengecek stabilitas.\n"
    "- KNN peka terhadap skala dan jumlah fitur (hasil one-hot menghasilkan puluhan dimensi) dan lambat pada data besar.\n"
    "- Evaluasi memakai satu kali pembagian latih/uji, bukan validasi silang."
)
