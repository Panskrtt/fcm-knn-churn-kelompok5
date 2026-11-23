"""
app.py - Aplikasi Streamlit: Segmentasi & Prediksi Churn Pelanggan Telco
         dengan kombinasi Fuzzy C-Means (FCM) dan K-Nearest Neighbor (KNN).

Jalankan lokal:  streamlit run app.py
"""
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.generate_sample_telco import generate
from modules import evaluation as ev
from modules.pipeline import ChurnFuzzyPipeline, Params
from modules.preprocessing import (COLUMN_DESCRIPTIONS, DataValidationError, NUMERIC_COLS,
                                   REQUIRED_COLUMNS, validate_dataframe)

st.set_page_config(page_title="FCM + KNN Prediksi Churn", layout="wide")

PAGES = ["Beranda", "Input Data", "Proses", "Hasil", "Evaluasi", "Prediksi", "Informasi Sistem"]
PALETTE = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6",
           "#06b6d4", "#ec4899", "#84cc16", "#f97316", "#64748b"]
REPO_DATASET = Path(__file__).parent / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
MANUAL_OPTIONS = {
    "gender": ["Female", "Male"],
    "Partner": ["Yes", "No"],
    "Dependents": ["Yes", "No"],
    "PhoneService": ["Yes", "No"],
    "MultipleLines": ["Yes", "No", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    "OnlineSecurity": ["Yes", "No", "No internet service"],
    "OnlineBackup": ["Yes", "No", "No internet service"],
    "DeviceProtection": ["Yes", "No", "No internet service"],
    "TechSupport": ["Yes", "No", "No internet service"],
    "StreamingTV": ["Yes", "No", "No internet service"],
    "StreamingMovies": ["Yes", "No", "No internet service"],
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": ["Yes", "No"],
    "PaymentMethod": ["Electronic check", "Mailed check",
                      "Bank transfer (automatic)", "Credit card (automatic)"],
    "Churn": ["Yes", "No"],
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

html, body, [class*="css"] {font-family:"DM Sans", "Segoe UI", sans-serif;}
.stApp {background:#f7f6f2; color:#292d32;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stMainBlockContainer"] {max-width:1440px; padding-top:2.5rem; padding-bottom:4rem;}
[data-testid="stSidebar"] {background:#f0eee8; border-right:1px solid #e3e0d8;}
[data-testid="stSidebar"] > div:first-child {padding-top:2rem;}
[data-testid="stSidebar"] h2 {font-family:"Newsreader", Georgia, serif; font-size:1.65rem; font-weight:500;}
h1, h2, h3 {color:#252a30; letter-spacing:-.025em;}
h1 {font-family:"Newsreader", Georgia, serif; font-size:2.35rem; font-weight:500; line-height:1.15;}
h2, h3 {font-weight:600;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e7e4dc; border-radius:10px; padding:1rem 1.1rem;}
[data-testid="stMetricLabel"] {color:#687078;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#e7e4dc; border-radius:10px;}
[data-testid="stTabs"] button {font-weight:600;}
[data-testid="stDataFrame"] {border:1px solid #e7e4dc; border-radius:8px;}
.stButton > button {border-radius:7px; font-weight:600; min-height:2.7rem;}
.stDownloadButton > button {border-radius:7px; font-weight:600;}
.hero {background:#fff; border:1px solid #e7e4dc; border-top:3px solid #58776d;
       color:#292d32; padding:2.3rem 2.5rem; border-radius:10px; margin-bottom:1.2rem;}
.hero small {color:#58776d; font-size:.75rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase;}
.hero h1 {font-family:"Newsreader", Georgia, serif; color:#252a30; margin:.75rem 0 .8rem;
          font-size:2.75rem; font-weight:500; line-height:1.08; letter-spacing:-.03em; padding:0;}
.hero p {color:#626a70; max-width:700px; line-height:1.7; margin:0;}
.chip {display:inline-block; background:#fff; border:1px solid #e3e0d8; color:#46524e; font-weight:600;
       padding:.35rem .7rem; border-radius:6px; margin:.15rem 0;}
.arrow {color:#89918e; margin:0 .3rem;}
.badge {display:inline-flex; align-items:center; justify-content:center; color:white; font-weight:700;
        border-radius:6px; width:2rem; height:2rem; margin-right:.6rem;}
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] {padding:1.5rem 1rem 3rem;}
    .hero {padding:1.6rem 1.35rem;}
    .hero h1 {font-size:2.15rem;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ helper
def show_df(df, **kw):
    st.dataframe(df, width="stretch", hide_index=True, **kw)


def show_plot(fig, height=420):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=10, r=10, t=40, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")


def go_to(page):
    st.session_state["page"] = page


def need_results():
    if st.session_state.results is None:
        st.info("Belum ada hasil. Muat dataset di **Input Data**, lalu jalankan **Proses**.")
        st.button("Ke menu Proses", on_click=go_to, args=("Proses",))
        return False
    return True


def init_state():
    defaults = {"df_raw": None, "dataset_name": None, "loaded_sig": None, "results": None,
                "pipeline": None, "logs": [], "history": [], "last_pred": None, "page": "Beranda"}
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def load_dataset(df, name, sig):
    try:
        validate_dataframe(df)
    except DataValidationError as e:
        st.error(f"Dataset tidak valid: {e}")
        return False
    st.session_state.update(df_raw=df, dataset_name=name, loaded_sig=sig, results=None,
                            pipeline=None, logs=[], last_pred=None)
    return True


def empty_manual_dataset():
    dtypes = {column: "object" for column in REQUIRED_COLUMNS}
    dtypes.update({column: "float64" for column in NUMERIC_COLS})
    dtypes["SeniorCitizen"] = "int64"
    return pd.DataFrame({column: pd.Series(dtype=dtypes[column]) for column in REQUIRED_COLUMNS})


# ------------------------------------------------------------------ halaman
def page_home():
    st.markdown("""
<div class="hero"><small>Analisis pelanggan · Telekomunikasi</small>
<h1>Memahami pola pelanggan,<br>lebih awal.</h1>
<p>Jelajahi segmen pelanggan dengan Fuzzy C-Means, lalu lihat bagaimana KNN memperkirakan risiko churn.
Mulai dengan dataset dan tinjau hasilnya sebagai bahan analisis.</p></div>""", unsafe_allow_html=True)
    st.button("Mulai: Input Data →", type="primary", on_click=go_to, args=("Input Data",))

    c1, c2, c3 = st.columns(3)
    for col, (t, d) in zip((c1, c2, c3), [
        ("1. Segmentasi Fuzzy", "FCM memberi tiap pelanggan derajat keanggotaan ke beberapa segmen sekaligus, bukan satu label kaku."),
        ("2. Prediksi dengan KNN", "Derajat keanggotaan ditambahkan sebagai fitur KNN untuk memprediksi churn."),
        ("3. Evaluasi Jelas", "Dibandingkan dengan KNN tanpa membership, lengkap dengan metrik dan interpretasi.")]):
        with col, st.container(border=True):
            st.subheader(t)
            st.write(d)

    st.subheader("Alur Metode")
    chips = ["Data", "Preprocessing", "FCM", "Membership (μ)", "KNN", "Prediksi"]
    st.markdown('<span class="arrow">→</span>'.join(f'<span class="chip">{c}</span>' for c in chips),
                unsafe_allow_html=True)

    st.subheader("Panduan Cepat")
    st.markdown("""
1. **Input Data**: unggah CSV, isi tabel manual (minimal 50 pelanggan), atau pakai dataset bawaan.
2. **Proses**: atur parameter, lalu jalankan.
3. **Hasil**: lihat segmentasi, tabel membership, dan interpretasi segmen.
4. **Evaluasi**: lihat metrik dan perbandingan baseline vs FCM + KNN.
5. **Prediksi**: coba prediksi satu pelanggan.
6. **Informasi Sistem**: penjelasan metode, rumus, dan parameter.""")


def page_data():
    st.title("Input Data")
    st.caption("Pilih cara memasukkan dataset Telco Customer Churn. Data divalidasi sebelum dipakai.")

    sources = ["Unggah file CSV", "Input manual (tabel)"]
    if REPO_DATASET.exists():
        sources.append("Dataset bawaan repo (Telco asli)")
    sources.append("Data Bawaan")
    src = st.radio("Sumber data", sources, horizontal=True)

    if src == "Unggah file CSV":
        f = st.file_uploader("Pilih file CSV", type=["csv"])
        if f is not None:
            sig = f"upload:{f.name}:{f.size}"
            if st.session_state.loaded_sig != sig:
                try:
                    df = pd.read_csv(f)
                except Exception as e:
                    st.error(f"File tidak dapat dibaca sebagai CSV: {e}")
                else:
                    if load_dataset(df, f.name, sig):
                        st.success("Dataset valid dan dimuat.")
    elif src == "Input manual (tabel)":
        st.info("Isi tabel langsung atau tempel data dari spreadsheet. Minimal 50 baris dengan nilai Churn 'Yes' dan 'No'.")
        with st.form("manual_dataset_form"):
            manual_df = st.data_editor(
                empty_manual_dataset(),
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                height=420,
                key="manual_dataset_editor",
                column_config={
                    "tenure": st.column_config.NumberColumn(
                        "Lama berlangganan (bulan)", min_value=0, max_value=120, step=1,
                        format="%d", required=True),
                    "SeniorCitizen": st.column_config.NumberColumn(
                        "Senior citizen (0/1)", min_value=0, max_value=1, step=1,
                        format="%d", required=True),
                    "MonthlyCharges": st.column_config.NumberColumn(
                        "Tagihan bulanan", min_value=0, format="%.2f", required=True),
                    "TotalCharges": st.column_config.NumberColumn(
                        "Total tagihan", min_value=0, format="%.2f",
                        help="Boleh dikosongkan; akan dihitung dari lama berlangganan × tagihan bulanan."),
                    **{
                        column: st.column_config.SelectboxColumn(
                            column, options=options, required=True)
                        for column, options in MANUAL_OPTIONS.items()
                    },
                },
            )
            manual_submitted = st.form_submit_button("Validasi & muat data manual", type="primary")
        if manual_submitted:
            entry_columns = [column for column in REQUIRED_COLUMNS if column != "TotalCharges"]
            incomplete = manual_df[entry_columns].isna().any(axis=1)
            if incomplete.any():
                st.error(f"Lengkapi semua kolom wajib pada {int(incomplete.sum())} baris sebelum memuat data.")
            elif load_dataset(manual_df, "Input manual", "manual"):
                st.success("Dataset manual valid dan dimuat.")
    elif src.startswith("Dataset bawaan"):
        if st.button("Muat dataset bawaan", type="primary"):
            if load_dataset(pd.read_csv(REPO_DATASET), REPO_DATASET.name, "repo"):
                st.success("Dataset bawaan dimuat.")
    elif src == "Data Bawaan":
        st.info("Data bawaan berisi 3.000 baris untuk demo. Data ini sintetis, bukan dataset Telco asli.")
        if st.button("Muat data bawaan", type="primary"):
            if load_dataset(generate(3000), "Data Bawaan", "sample"):
                st.success("Data bawaan dimuat.")

    df = st.session_state.df_raw
    if df is None:
        st.info("Belum ada dataset yang dimuat.")
    else:
        churn = (df["Churn"].astype(str).str.strip() == "Yes").mean() * 100
        st.subheader(f"Dataset aktif: {st.session_state.dataset_name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Jumlah baris", f"{len(df):,}")
        c2.metric("Jumlah kolom", df.shape[1])
        c3.metric("Tingkat churn", f"{churn:.1f}%")
        st.subheader("Pratinjau (50 baris pertama)")
        show_df(df.head(50))
        st.button("Lanjut ke Proses →", type="primary", on_click=go_to, args=("Proses",))

    with st.expander("Penjelasan variabel"):
        show_df(pd.DataFrame({"Variabel": list(COLUMN_DESCRIPTIONS), "Penjelasan": list(COLUMN_DESCRIPTIONS.values())}))


def page_process():
    st.title("Proses Pengolahan")
    st.caption("Atur parameter lalu jalankan alur FCM → KNN.")
    df = st.session_state.df_raw
    if df is None:
        st.info("Muat dataset terlebih dahulu di menu **Input Data**.")
        st.button("Ke Input Data", on_click=go_to, args=("Input Data",))
        return

    d = Params()
    with st.form("params"):
        st.subheader("Parameter")
        c1, c2, c3, c4 = st.columns(4)
        n_clusters = c1.number_input("Jumlah cluster (c)", 2, 10, d.n_clusters, 1, help="2 - 10")
        m = c2.number_input("Fuzzifier (m)", 1.01, 5.0, d.m, 0.1, help="> 1 dan ≤ 5")
        tol = c3.number_input("Toleransi (epsilon)", 1e-8, 0.1, d.tol, 1e-5, format="%.1e")
        max_iter = c4.number_input("Iterasi maksimum", 1, 1000, d.max_iter, 10)
        c5, c6, c7, c8 = st.columns(4)
        k = c5.number_input("Tetangga KNN (k)", 1, 50, d.k, 1)
        test_size = c6.number_input("Proporsi data uji", 0.1, 0.5, d.test_size, 0.05)
        weight = c7.number_input("Bobot fitur membership", 0.0, 10.0, d.membership_weight, 0.5)
        seed = c8.number_input("Random state", 0, 10_000, d.random_state, 1)
        submitted = st.form_submit_button("Jalankan proses", type="primary")

    with st.expander("Tahapan pengolahan"):
        st.markdown("""
1. Validasi dan pembersihan data (TotalCharges kosong diisi tenure × MonthlyCharges).
2. Pembagian data latih/uji secara stratified agar proporsi churn terjaga.
3. One-hot encoding fitur kategorikal dan standarisasi z-score fitur numerik (dari data latih saja).
4. FCM pada tenure, MonthlyCharges, TotalCharges: hitung pusat cluster dan perbarui U sampai konvergen.
5. Hitung derajat keanggotaan data latih dan data uji terhadap pusat cluster.
6. KNN gabungan memakai [fitur asli | bobot × membership]; KNN baseline tanpa membership.
7. Evaluasi: akurasi, precision, recall, F1, confusion matrix, silhouette, PC, PE.""")

    if submitted:
        params = Params(n_clusters=int(n_clusters), m=float(m), tol=float(tol), max_iter=int(max_iter),
                        k=int(k), test_size=float(test_size), membership_weight=float(weight),
                        random_state=int(seed))
        logs = []
        pipe = ChurnFuzzyPipeline()
        with st.status("Menjalankan FCM + KNN ...", expanded=True) as status:
            bar = st.progress(0.0)

            def log(text):
                logs.append(text)
                st.write(text)
                if text.startswith("[") and "/7]" in text:
                    bar.progress(int(text[1:text.index("/")]) / 7)
            try:
                res = pipe.run(df, params, log=log)
            except (DataValidationError, ValueError) as e:
                status.update(label="Proses gagal", state="error")
                st.error(str(e))
                return
            bar.progress(1.0)
            status.update(label="Proses selesai", state="complete", expanded=False)
        st.session_state.update(results=res, pipeline=pipe, logs=logs, last_pred=None)
        st.success("Selesai. Lihat menu Hasil dan Evaluasi.")

    res = st.session_state.results
    if res is not None:
        hist = res["fcm"].history_
        fig = go.Figure(go.Scatter(x=[h[0] for h in hist], y=[h[1] for h in hist], mode="lines",
                                   line=dict(color=PALETTE[0], width=2)))
        fig.update_layout(title="Konvergensi Fuzzy C-Means", xaxis_title="Iterasi", yaxis_title="Fungsi objektif J")
        show_plot(fig, 320)
        with st.expander("Log proses"):
            st.code("\n".join(st.session_state.logs))
        c1, c2 = st.columns(2)
        c1.button("Lihat Hasil →", type="primary", on_click=go_to, args=("Hasil",))
        c2.button("Lihat Evaluasi →", on_click=go_to, args=("Evaluasi",))


def page_results():
    st.title("Hasil Pengolahan")
    if not need_results():
        return
    r = st.session_state.results
    v, p = r["validity"], r["params"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah cluster", p.n_clusters, f"m = {p.m}", delta_color="off")
    c2.metric("Iterasi FCM", v["iterations"], "konvergen" if v["converged"] else "belum konvergen",
              delta_color="normal" if v["converged"] else "inverse")
    c3.metric("Silhouette", "n/a" if v["silhouette"] is None else f"{v['silhouette']:.3f}")
    c4.metric("Partition Coefficient", f"{v['pc']:.3f}")

    tab1, tab2, tab3 = st.tabs(["Segmentasi", "Membership & Prediksi", "Interpretasi"])

    with tab1:
        df, labels = r["df_train"], r["labels_train"]
        idx = np.random.default_rng(0).choice(len(df), min(len(df), 2500), replace=False)
        fig = go.Figure()
        for j in range(p.n_clusters):
            sel = idx[labels[idx] == j]
            fig.add_trace(go.Scatter(x=df["tenure"].to_numpy()[sel], y=df["MonthlyCharges"].to_numpy()[sel],
                                     mode="markers", name=f"Cluster {j + 1}",
                                     marker=dict(color=PALETTE[j % 10], size=6, opacity=0.6)))
        c = r["centers_orig"]
        fig.add_trace(go.Scatter(x=c[:, 0], y=c[:, 1], mode="markers", name="Pusat cluster",
                                 marker=dict(color="#0f172a", size=15, symbol="x", line=dict(color="white", width=1.5))))
        fig.update_layout(title="Segmentasi FCM (warna = keanggotaan tertinggi)",
                          xaxis_title="Tenure (bulan)", yaxis_title="MonthlyCharges ($)")
        show_plot(fig, 480)
        rows = []
        for q in r["profile"]:
            ctr = r["centers_orig"][q["cluster"] - 1]
            rows.append({"Cluster": f"Cluster {q['cluster']}", "Jumlah": q["n"], "Porsi (%)": round(q["pct"], 1),
                         "Pusat tenure": round(ctr[0], 1), "Pusat MonthlyCharges": round(ctr[1], 2),
                         "Pusat TotalCharges": round(ctr[2], 1), "Churn (%)": round(q["churn"] * 100, 1)})
        st.subheader("Pusat cluster dan profil segmen")
        show_df(pd.DataFrame(rows))

    with tab2:
        U, n = r["U_test"], r["U_test"].shape[0]
        data = {f"μ Cluster {j + 1}": U[:, j] for j in range(p.n_clusters)}
        data["Cluster dominan"] = [f"Cluster {int(i) + 1}" for i in U.argmax(axis=1)]
        data["Aktual"] = np.where(r["y_test"] == 1, "Churn", "Tidak")
        data["Prediksi FCM+KNN"] = np.where(r["pred_comb"] == 1, "Churn", "Tidak")
        mem = pd.DataFrame(data)
        st.caption(f"Data uji: {n} pelanggan. Tampilan menunjukkan 300 baris pertama; unduh untuk data lengkap.")
        cfg = {f"μ Cluster {j + 1}": st.column_config.ProgressColumn(min_value=0.0, max_value=1.0, format="%.3f")
               for j in range(p.n_clusters)}
        show_df(mem.head(300), column_config=cfg)
        st.download_button("Unduh membership data uji (CSV)", mem.to_csv(index=False).encode(),
                           "membership_data_uji.csv", "text/csv")

    with tab3:
        lines = r["text_clusters"].split("\n")
        k = len(r["profile"])
        for q, line in zip(r["profile"], lines[:k]):
            with st.container(border=True):
                st.markdown(f'<span class="badge" style="background:{PALETTE[(q["cluster"] - 1) % 10]}">C{q["cluster"]}</span>'
                            f"{line}", unsafe_allow_html=True)
        st.caption("\n".join(lines[k:]).strip())


def page_eval():
    st.title("Evaluasi")
    if not need_results():
        return
    r = st.session_state.results
    b, g, v = r["metrics_base"], r["metrics_comb"], r["validity"]

    cols = st.columns(4)
    for col, (label, key) in zip(cols, [("Akurasi", "accuracy"), ("Precision churn", "precision"),
                                         ("Recall churn", "recall"), ("F1 churn", "f1")]):
        col.metric(label, f"{g[key]:.3f}", f"{(g[key] - b[key]) * 100:+.1f} poin vs baseline")

    st.subheader("Metrik klasifikasi")
    st.caption("Kelas churn sebagai kelas positif, dihitung pada data uji.")
    show_df(pd.DataFrame([
        {"Model": "KNN baseline (tanpa membership)", "Akurasi": b["accuracy"], "Precision": b["precision"],
         "Recall": b["recall"], "F1": b["f1"]},
        {"Model": "FCM + KNN (gabungan)", "Akurasi": g["accuracy"], "Precision": g["precision"],
         "Recall": g["recall"], "F1": g["f1"]}]).round(3))

    st.subheader("Kualitas clustering FCM (data latih)")
    show_df(pd.DataFrame([{"Silhouette": "n/a" if v["silhouette"] is None else round(v["silhouette"], 3),
                           "Partition Coefficient": round(v["pc"], 3), "Partition Entropy": round(v["pe"], 3),
                           "J akhir": round(v["J"], 2), "Iterasi": v["iterations"],
                           "Konvergen": "Ya" if v["converged"] else "Tidak"}]))

    c1, c2 = st.columns(2)
    with c1:
        names, keys = ["Akurasi", "Precision", "Recall", "F1"], ["accuracy", "precision", "recall", "f1"]
        fig = go.Figure([go.Bar(name="Baseline", x=names, y=[b[k] for k in keys], marker_color="#cbd5e1"),
                         go.Bar(name="FCM + KNN", x=names, y=[g[k] for k in keys], marker_color=PALETTE[0])])
        fig.update_layout(title="Perbandingan metrik", barmode="group", yaxis=dict(range=[0, 1]))
        show_plot(fig, 380)
    with c2:
        cm = g["confusion_matrix"]
        fig = go.Figure(go.Heatmap(z=cm, x=["Tidak", "Churn"], y=["Tidak", "Churn"], colorscale="Blues",
                                   text=cm, texttemplate="%{text}", textfont=dict(size=20), showscale=False))
        fig.update_layout(title="Confusion matrix FCM + KNN", xaxis_title="Prediksi", yaxis_title="Aktual",
                          yaxis=dict(autorange="reversed"))
        show_plot(fig, 380)

    st.subheader("Analisis")
    d_f1 = g["f1"] - b["f1"]
    box = st.success if d_f1 > 0.005 else st.warning if d_f1 < -0.005 else st.info
    box(r["text_comparison"])
    st.markdown(ev.LIMITATIONS)


def page_predict():
    st.title("Prediksi Pelanggan")
    if not need_results():
        return
    r, pipe = st.session_state.results, st.session_state.pipeline
    prep = r["prep"]
    st.caption("Masukkan data satu pelanggan. Kolom lain diisi nilai paling umum dari data latih.")

    def choice(label, col, options=None):
        opts = list(options if options is not None else prep.levels[col])
        default = prep.defaults.get(col, opts[0])
        return st.selectbox(label, opts, index=opts.index(default) if default in opts else 0)

    with st.form("predict"):
        c1, c2, c3 = st.columns(3)
        tenure = c1.number_input("Lama berlangganan (bulan)", 0, 120, 12, 1)
        monthly = c2.number_input("Tagihan bulanan ($)", 0.01, 1000.0, 70.0, 1.0)
        total = c3.number_input("Total tagihan ($), 0 = otomatis", 0.0, 1_000_000.0, 0.0, 10.0)
        c4, c5, c6 = st.columns(3)
        with c4:
            senior = choice("Senior citizen", "SeniorCitizen", [0, 1])
            contract = choice("Kontrak", "Contract")
        with c5:
            internet = choice("Layanan internet", "InternetService")
            payment = choice("Metode pembayaran", "PaymentMethod")
        with c6:
            paperless = choice("Tagihan tanpa kertas", "PaperlessBilling")
            tech = choice("Dukungan teknis", "TechSupport")
        security = choice("Keamanan online", "OnlineSecurity")
        go_btn = st.form_submit_button("Prediksi Pelanggan", type="primary")

    if go_btn:
        values = {"tenure": int(tenure), "MonthlyCharges": float(monthly),
                  "TotalCharges": float(total) if total > 0 else float(tenure) * float(monthly),
                  "SeniorCitizen": int(senior), "Contract": contract, "InternetService": internet,
                  "PaymentMethod": payment, "PaperlessBilling": paperless, "TechSupport": tech,
                  "OnlineSecurity": security}
        out = pipe.predict_one(values)
        prof = next((q for q in r["profile"] if q["cluster"] == out["cluster"]), None)
        out["cluster_churn_rate"] = prof["churn"] if prof else None
        st.session_state.last_pred = out
        st.session_state.history.insert(0, {
            "Waktu": datetime.now().strftime("%d %b %H:%M:%S"), "Tenure": values["tenure"],
            "Tagihan": values["MonthlyCharges"], "Kontrak": contract, "Cluster": out["cluster"],
            "Hasil": "Churn" if out["pred"] else "Bertahan", "Baseline": "Churn" if out["pred_base"] else "Bertahan",
            "Proporsi churn (%)": round(out["proba_churn"] * 100)})

    out = st.session_state.last_pred
    if out:
        pct = out["proba_churn"] * 100
        if out["pred"]:
            st.error(f"**Berisiko churn** · {pct:.0f}% tetangga terdekat churn")
        else:
            st.success(f"**Kemungkinan bertahan** · {pct:.0f}% tetangga terdekat churn")
        c1, c2 = st.columns([3, 2])
        with c1:
            mu = out["membership"]
            fig = go.Figure(go.Bar(x=mu, y=[f"Cluster {i + 1}" for i in range(len(mu))], orientation="h",
                                   marker_color=[PALETTE[i % 10] for i in range(len(mu))],
                                   text=[f"{x:.3f}" for x in mu], textposition="auto"))
            fig.update_layout(title="Derajat keanggotaan", xaxis=dict(range=[0, 1]), yaxis=dict(autorange="reversed"))
            show_plot(fig, 260)
        with c2:
            st.metric("Cluster dominan", f"Cluster {out['cluster']}")
            st.metric("Prediksi KNN baseline", "Churn" if out["pred_base"] else "Bertahan")
            if out["cluster_churn_rate"] is not None:
                st.metric("Churn historis segmen", f"{out['cluster_churn_rate'] * 100:.1f}%")

    if st.session_state.history:
        st.subheader("Riwayat prediksi (sesi ini)")
        hist = pd.DataFrame(st.session_state.history)
        show_df(hist)
        st.download_button("Unduh riwayat (CSV)", hist.to_csv(index=False).encode(), "riwayat_prediksi.csv", "text/csv")
        st.caption("Riwayat tersimpan selama sesi browser dan hilang jika halaman dimuat ulang.")


def page_info():
    st.title("Informasi Sistem")
    st.header("Fuzzy C-Means (FCM)")
    st.write("Input: matriks data numerik X (tenure, MonthlyCharges, TotalCharges yang distandarisasi). "
             "Parameter: jumlah cluster c, fuzzifier m (>1), epsilon, iterasi maksimum.")
    st.latex(r"J = \sum_{i=1}^{N}\sum_{j=1}^{c} u_{ij}^{m}\,\lVert x_i - c_j\rVert^2")
    st.latex(r"c_j = \frac{\sum_i u_{ij}^{m} x_i}{\sum_i u_{ij}^{m}}")
    st.latex(r"u_{ij} = \frac{1}{\sum_{k=1}^{c}\left(\frac{\lVert x_i - c_j\rVert}{\lVert x_i - c_k\rVert}\right)^{\frac{2}{m-1}}}")
    st.write("Iterasi: ulangi pembaruan pusat dan U sampai max|U_baru − U_lama| < epsilon. "
             "Output: pusat cluster dan matriks keanggotaan U (tiap baris berjumlah 1).")
    st.header("K-Nearest Neighbor (KNN)")
    st.write("Input: fitur asli terstandarisasi (one-hot + numerik) digabung dengan bobot × derajat keanggotaan FCM. "
             "Parameter: jumlah tetangga k dan bobot fitur membership. Proses: jarak Euclidean ke seluruh data latih, "
             "ambil k tetangga terdekat, voting mayoritas. Output: prediksi churn dan proporsi tetangga churn.")
    st.header("Integrasi FCM dan KNN")
    st.write("FCM dilatih pada data latih saja. Derajat keanggotaan data latih, data uji, dan data baru dihitung "
             "terhadap pusat cluster yang sama, lalu ditambahkan sebagai kolom fitur KNN. KNN baseline (tanpa kolom "
             "membership) dilatih pada pembagian data yang sama sebagai pembanding.")
    st.header("Library")
    st.markdown("- **NumPy**: operasi matriks FCM (ditulis mandiri)\n- **Pandas**: membaca dan membersihkan data\n"
                "- **scikit-learn**: StandardScaler, train_test_split, KNeighborsClassifier, metrik\n"
                "- **Plotly**: grafik interaktif\n- **Streamlit**: antarmuka web")


# ------------------------------------------------------------------ main
init_state()
with st.sidebar:
    st.markdown("## Telco Churn")
    st.caption("Segmentasi dan prediksi")
    st.radio("Menu", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    df_s = st.session_state.df_raw
    st.write(("Dataset: " + f"{len(df_s):,} baris") if df_s is not None else "Dataset belum dimuat")
    st.write("Model sudah dilatih" if st.session_state.results is not None else "Model belum dilatih")

{"Beranda": page_home, "Input Data": page_data, "Proses": page_process, "Hasil": page_results,
 "Evaluasi": page_eval, "Prediksi": page_predict, "Informasi Sistem": page_info}[st.session_state.page]()
