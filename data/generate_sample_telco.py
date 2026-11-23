"""
generate_sample_telco.py - Membuat data SINTETIS berformat Telco Customer Churn.

HANYA untuk menguji aplikasi tanpa dataset asli. Jangan dipakai sebagai data laporan.
Untuk laporan, gunakan dataset asli (WA_Fn-UseC_-Telco-Customer-Churn.csv, IBM sample data / Kaggle).

Pemakaian:  python data/generate_sample_telco.py  ->  data/sample_telco_synthetic.csv
"""
import os

import numpy as np
import pandas as pd


def generate(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    tenure = rng.integers(0, 73, n)
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22])
    contract = np.where(tenure > 40, rng.choice(["One year", "Two year"], n),
                        rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.75, 0.15, 0.10]))
    base = {"DSL": 45, "Fiber optic": 80, "No": 22}
    monthly = np.array([base[i] for i in internet]) + rng.normal(0, 6, n)
    monthly = np.clip(monthly, 18.25, 119).round(2)
    total = (tenure * monthly * rng.uniform(0.95, 1.05, n)).round(2)

    def yn(p):
        return rng.choice(["Yes", "No"], n, p=[p, 1 - p])

    def svc(p):
        return np.where(internet == "No", "No internet service", yn(p))

    logit = (-1.0 - 0.04 * tenure + 0.015 * (monthly - 65)
             + np.where(contract == "Month-to-month", 1.0, -0.6)
             + np.where(internet == "Fiber optic", 0.4, 0.0))
    churn = np.where(rng.random(n) < 1 / (1 + np.exp(-logit)), "Yes", "No")

    df = pd.DataFrame({
        "customerID": [f"SYN-{i:05d}" for i in range(n)],
        "gender": rng.choice(["Male", "Female"], n),
        "SeniorCitizen": rng.choice([0, 1], n, p=[0.84, 0.16]),
        "Partner": yn(0.48), "Dependents": yn(0.3), "tenure": tenure,
        "PhoneService": yn(0.9), "MultipleLines": rng.choice(["Yes", "No", "No phone service"], n),
        "InternetService": internet, "OnlineSecurity": svc(0.3), "OnlineBackup": svc(0.35),
        "DeviceProtection": svc(0.35), "TechSupport": svc(0.3), "StreamingTV": svc(0.4),
        "StreamingMovies": svc(0.4), "Contract": contract, "PaperlessBilling": yn(0.6),
        "PaymentMethod": rng.choice(["Electronic check", "Mailed check",
                                     "Bank transfer (automatic)", "Credit card (automatic)"], n),
        "MonthlyCharges": monthly, "TotalCharges": total, "Churn": churn,
    })
    # meniru dataset asli: TotalCharges berupa string, kosong (" ") bila tenure = 0
    df["TotalCharges"] = df["TotalCharges"].astype(str)
    df.loc[df["tenure"] == 0, "TotalCharges"] = " "
    return df


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_telco_synthetic.csv")
    generate().to_csv(out, index=False)
    print("Tersimpan:", out)
