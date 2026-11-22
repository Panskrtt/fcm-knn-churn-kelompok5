"""Uji API end-to-end. Jalankan dari folder churn-api:  python tests/test_api.py"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient  # noqa: E402

from data.generate_sample_telco import generate  # noqa: E402
from main import app  # noqa: E402

c = TestClient(app)
csv = generate(1500).to_csv(index=False).encode()

assert c.get("/health").json() == {"status": "ok"}

r = c.post("/inspect", files={"file": ("telco.csv", csv, "text/csv")})
assert r.status_code == 200 and r.json()["n_rows"] == 1500, r.text
print("inspect OK:", r.json()["n_rows"], "baris, churn", round(r.json()["churn_rate"], 3))

bad = c.post("/inspect", files={"file": ("x.csv", b"a,b\n1,2\n", "text/csv")})
assert bad.status_code == 422, bad.text
print("inspect CSV salah ->", bad.json()["detail"].splitlines()[0])

r = c.post("/train", files={"file": ("telco.csv", csv, "text/csv")},
           data={"n_clusters": 3, "m": 2.0, "tol": "1e-05", "max_iter": 300, "k": 5, "test_size": 0.2,
                 "membership_weight": 1.0, "random_state": 42})
assert r.status_code == 200, r.text
res = r.json()
for key in ("model_id", "metrics_base", "metrics_comb", "validity", "profile", "centers", "history",
            "scatter", "test_rows", "text_clusters", "text_comparison", "limitations", "logs"):
    assert key in res, key
print("train OK: iterasi", res["validity"]["iterations"], "| F1 base/gabungan",
      round(res["metrics_base"]["f1"], 3), round(res["metrics_comb"]["f1"], 3),
      "| scatter", len(res["scatter"]), "| test_rows", len(res["test_rows"]))

bad = c.post("/train", files={"file": ("telco.csv", csv, "text/csv")}, data={"m": 0.5})
assert bad.status_code == 422, bad.text
print("train parameter salah ->", bad.json()["detail"])

mid = res["model_id"]
r = c.post("/predict", json={"model_id": mid, "values": {
    "tenure": 3, "MonthlyCharges": 85.0, "TotalCharges": 255.0, "SeniorCitizen": 0,
    "Contract": "Month-to-month", "InternetService": "Fiber optic"}})
assert r.status_code == 200, r.text
out = r.json()
assert abs(sum(out["membership"]) - 1) < 1e-6
print("predict OK:", {k: out[k] for k in ("cluster", "pred", "proba_churn", "pred_base")})

for payload, label in [({"model_id": mid, "values": {"Contract": "Seumur hidup"}}, "kategori salah"),
                       ({"model_id": mid, "values": {"tenure": "abc"}}, "angka salah"),
                       ({"model_id": mid, "values": {"hack": 1}}, "kolom asing"),
                       ({"model_id": "../../etc/passwd", "values": {}}, "model_id berbahaya"),
                       ({"model_id": "0" * 32, "values": {}}, "model tidak ada")]:
    r = c.post("/predict", json=payload)
    assert r.status_code in (404, 422), (label, r.text)
    print(f"predict {label} -> {r.status_code}")

assert c.delete(f"/models/{mid}").json()["deleted"]
assert c.post("/predict", json={"model_id": mid, "values": {}}).status_code == 404
print("API TEST LULUS")
