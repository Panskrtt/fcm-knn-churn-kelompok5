"""
fcm.py - Implementasi Fuzzy C-Means (FCM) mandiri dengan NumPy.

Rumus utama:
  Fungsi objektif : J = sum_i sum_j (u_ij ** m) * ||x_i - c_j||^2
  Pusat cluster   : c_j = sum_i (u_ij ** m) * x_i / sum_i (u_ij ** m)
  Keanggotaan     : u_ij = 1 / sum_k ( ||x_i - c_j|| / ||x_i - c_k|| ) ** (2 / (m - 1))
"""
import numpy as np


class FuzzyCMeans:
    def __init__(self, n_clusters=3, m=2.0, max_iter=100, tol=1e-5, random_state=42):
        if m <= 1:
            raise ValueError("Parameter fuzzifier m harus > 1.")
        if n_clusters < 2:
            raise ValueError("Jumlah cluster minimal 2.")
        self.c = n_clusters
        self.m = m
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centers_ = None      # (c, d)
        self.U_ = None            # (n, c) matriks keanggotaan
        self.history_ = []        # riwayat iterasi: (iterasi, J, delta U)

    # ---------- langkah-langkah algoritma ----------
    @staticmethod
    def _distance(X, centers):
        """Jarak Euclidean tiap data ke tiap pusat -> (n, c)."""
        d = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
        return np.fmax(d, 1e-10)  # hindari pembagian nol

    def _init_membership(self, n):
        """Langkah 1: inisialisasi U acak, tiap baris dijumlah = 1."""
        rng = np.random.default_rng(self.random_state)
        U = rng.random((n, self.c))
        return U / U.sum(axis=1, keepdims=True)

    def _update_centers(self, X, U):
        """Langkah 2: hitung pusat cluster dari U^m."""
        Um = U ** self.m
        return (Um.T @ X) / Um.sum(axis=0)[:, None]

    def _update_membership(self, X, centers):
        """Langkah 3: perbarui U dari jarak ke pusat cluster."""
        d = self._distance(X, centers)
        inv = d ** (-2.0 / (self.m - 1.0))
        return inv / inv.sum(axis=1, keepdims=True)

    def _objective(self, X, U, centers):
        d = self._distance(X, centers)
        return float(np.sum((U ** self.m) * d ** 2))

    # ---------- API publik ----------
    def fit(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[0] < self.c:
            raise ValueError("Data harus 2 dimensi dengan jumlah baris >= jumlah cluster.")
        U = self._init_membership(X.shape[0])
        self.history_ = []
        for it in range(1, self.max_iter + 1):
            centers = self._update_centers(X, U)
            J = self._objective(X, U, centers)
            U_new = self._update_membership(X, centers)
            delta = float(np.max(np.abs(U_new - U)))  # Langkah 4: cek konvergensi
            self.history_.append((it, J, delta))
            U = U_new
            if delta < self.tol:
                break
        self.centers_ = self._update_centers(X, U)
        self.U_ = U
        return self

    def predict_membership(self, X_new):
        """Derajat keanggotaan data baru terhadap pusat cluster yang sudah dilatih."""
        if self.centers_ is None:
            raise RuntimeError("Model belum dilatih. Jalankan fit() terlebih dahulu.")
        return self._update_membership(np.asarray(X_new, dtype=float), self.centers_)

    def predict(self, X_new):
        """Label cluster (hard) = cluster dengan keanggotaan tertinggi."""
        return np.argmax(self.predict_membership(X_new), axis=1)

    @property
    def labels_(self):
        return np.argmax(self.U_, axis=1)

    # ---------- indeks validitas cluster ----------
    def partition_coefficient(self):
        """PC = (1/N) sum u^2. Rentang 1/c .. 1, makin besar makin tegas."""
        return float(np.mean(np.sum(self.U_ ** 2, axis=1)))

    def partition_entropy(self):
        """PE = -(1/N) sum u log(u). Makin kecil makin tegas."""
        U = np.fmax(self.U_, 1e-12)
        return float(-np.mean(np.sum(U * np.log(U), axis=1)))


if __name__ == "__main__":
    # Uji cepat dengan data sintetis 3 kelompok
    rng = np.random.default_rng(0)
    X = np.vstack([
        rng.normal([0, 0], 0.5, (50, 2)),
        rng.normal([4, 4], 0.5, (50, 2)),
        rng.normal([0, 4], 0.5, (50, 2)),
    ])
    model = FuzzyCMeans(n_clusters=3, m=2.0).fit(X)
    print("Iterasi        :", len(model.history_))
    print("Pusat cluster  :\n", np.round(model.centers_, 3))
    print("PC / PE        : %.3f / %.3f" % (model.partition_coefficient(), model.partition_entropy()))
    print("Membership data[0]:", np.round(model.U_[0], 3), "| jumlah =", round(model.U_[0].sum(), 3))
