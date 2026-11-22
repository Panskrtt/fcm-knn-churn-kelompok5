"""
classifier.py - KNN yang memakai derajat keanggotaan FCM sebagai fitur tambahan.

Integrasi FCM -> KNN:
  fitur KNN = [ fitur asli terstandarisasi | bobot * (mu_1 ... mu_c) ]
  Jarak Euclidean KNN dengan demikian ikut mempertimbangkan kedekatan data pada cluster fuzzy.
"""
import numpy as np
from sklearn.neighbors import KNeighborsClassifier


def combine_features(X_base, U, weight=1.0):
    return np.hstack([X_base, weight * U])


class MembershipKNN:
    def __init__(self, k=5, weight=1.0, use_membership=True):
        self.k = k
        self.weight = weight
        self.use_membership = use_membership
        self.model = None

    def _build(self, X_base, U):
        return combine_features(X_base, U, self.weight) if self.use_membership else X_base

    def fit(self, X_base, U, y):
        self.model = KNeighborsClassifier(n_neighbors=self.k, metric="euclidean")
        self.model.fit(self._build(X_base, U), y)
        return self

    def predict(self, X_base, U):
        return self.model.predict(self._build(X_base, U))

    def predict_proba_churn(self, X_base, U):
        proba = self.model.predict_proba(self._build(X_base, U))
        classes = list(self.model.classes_)
        return proba[:, classes.index(1)] if 1 in classes else np.zeros(len(proba))
