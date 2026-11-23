"""Uji end-to-end antarmuka Streamlit tanpa browser (streamlit.testing).
Jalankan dari folder proyek:  python tests/test_app.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import pandas as pd  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402
from data.generate_sample_telco import generate  # noqa: E402


def ok(at, label):
    assert not at.exception, f"{label}: {[e.value for e in at.exception]}"
    print(f"OK  {label}")


def button(at, label):
    return next(b for b in at.button if b.label == label)


at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=300).run()
ok(at, "Beranda")

# halaman yang butuh hasil, dibuka sebelum ada data -> harus menampilkan info, bukan error
for page in ["Proses", "Hasil", "Evaluasi", "Prediksi"]:
    at.sidebar.radio[0].set_value(page).run()
    ok(at, f"{page} tanpa data")
    assert at.info, f"{page}: seharusnya ada pesan info"

at.sidebar.radio[0].set_value("Input Data").run()
ok(at, "Input Data")
at.main.radio[0].set_value("Input manual (tabel)").run()
ok(at, "Input manual")
button(at, "Validasi & muat data manual").click().run()
ok(at, "Validasi input manual kosong")
assert any("Dataset kosong" in error.value for error in at.error)
assert at.session_state["df_raw"] is None

manual_df = generate(50).drop(columns=["customerID"])
manual_df["TotalCharges"] = pd.to_numeric(manual_df["TotalCharges"], errors="coerce")
at.session_state["manual_dataset_editor"] = {
    "edited_rows": {}, "added_rows": manual_df.to_dict(orient="records"), "deleted_rows": []
}
button(at, "Validasi & muat data manual").click().run()
ok(at, "Muat dataset manual")
assert at.session_state["dataset_name"] == "Input manual"
assert len(at.session_state["df_raw"]) == 50

at.main.radio[0].set_value("Data Bawaan").run()
ok(at, "Data Bawaan")
button(at, "Muat data bawaan").click().run()
ok(at, "Muat data bawaan")
assert at.session_state["df_raw"] is not None and len(at.session_state["df_raw"]) == 3000

at.sidebar.radio[0].set_value("Proses").run()
ok(at, "Proses (form)")
button(at, "Jalankan proses").click().run()
ok(at, "Jalankan proses")
res = at.session_state["results"]
assert res is not None
print("    F1 baseline/gabungan:", round(res["metrics_base"]["f1"], 3), round(res["metrics_comb"]["f1"], 3),
      "| iterasi", res["validity"]["iterations"], "| konvergen", res["validity"]["converged"])

for page in ["Hasil", "Evaluasi"]:
    at.sidebar.radio[0].set_value(page).run()
    ok(at, page)

at.sidebar.radio[0].set_value("Prediksi").run()
ok(at, "Prediksi (form)")
button(at, "Prediksi Pelanggan").click().run()
ok(at, "Prediksi pelanggan")
out = at.session_state["last_pred"]
assert abs(sum(out["membership"]) - 1) < 1e-6 and len(at.session_state["history"]) == 1
print("    hasil:", {k: out[k] for k in ("cluster", "pred", "proba_churn")})

# ubah parameter (c = 4, m = 1.5) lalu proses ulang
at.sidebar.radio[0].set_value("Proses").run()
at.number_input[0].set_value(4)
at.number_input[1].set_value(1.5)
button(at, "Jalankan proses").click().run()
ok(at, "Proses ulang c=4, m=1.5")
assert at.session_state["results"]["params"].n_clusters == 4

at.sidebar.radio[0].set_value("Informasi Sistem").run()
ok(at, "Informasi Sistem")
print("UJI STREAMLIT LULUS")
