"""Datasets, detectors and evaluation for account-window manipulation detection."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler

from .features import FEATURES, label_windows, window_features
from .sim import SimConfig, manipulation_impact, run_episode, tagged_pnl_per_share

WINDOW = 300


def _one(args):
    seed, cfg = args
    ep = run_episode(seed, cfg)
    df = label_windows(ep, window_features(ep, WINDOW), WINDOW)
    df["episode"] = seed
    pnl = {}
    for name, prefix in (("spoof", "spoof_"), ("pump", "pd_")):
        per_share, shares = tagged_pnl_per_share(ep, prefix)
        pnl[name] = (0.0 if shares == 0 else per_share * shares, shares)
    pnl["impact"] = manipulation_impact(ep)
    return df, pnl


def build_dataset(seeds, cfg: SimConfig, workers: int = 4):
    """Simulate `seeds` and return (windows dataframe, {type: (total_pnl, shares)})."""
    with ProcessPoolExecutor(workers) as pool:
        results = list(pool.map(_one, [(s, cfg) for s in seeds]))
    df = pd.concat([r[0] for r in results], ignore_index=True)
    pnl = {k: (sum(r[1][k][0] for r in results), sum(r[1][k][1] for r in results)) for k in ("spoof", "pump")}
    pnl["impact"] = {k: [x for r in results for x in r[1]["impact"][k]] for k in ("spoof", "pump")}
    return df, pnl


def with_evasion(cfg: SimConfig, evasion: float) -> SimConfig:
    return replace(cfg, evasion=evasion)


# -- detectors -------------------------------------------------------------
def _slog(x):
    return np.sign(x) * np.log1p(np.abs(x))


class Detector:
    name = "base"
    supervised = True

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "Detector":
        return self

    def score(self, X: pd.DataFrame) -> np.ndarray:  # higher = more suspicious
        raise NotImplementedError


class OTRRule(Detector):
    """Order-to-trade ratio: the classic exchange surveillance indicator."""

    name = "otr_rule"
    supervised = False

    def score(self, X):
        return X["otr"].to_numpy()


class Logistic(Detector):
    name = "logreg"

    def fit(self, X, y):
        self.sc = StandardScaler().fit(_slog(X[FEATURES].to_numpy()))
        self.m = LogisticRegression(class_weight="balanced", max_iter=3000, C=1.0).fit(
            self.sc.transform(_slog(X[FEATURES].to_numpy())), y)
        return self

    def score(self, X):
        return self.m.decision_function(self.sc.transform(_slog(X[FEATURES].to_numpy())))


class GBM(Detector):
    name = "gbm"

    def __init__(self, seed: int = 0):
        self.seed = seed

    def fit(self, X, y):
        self.m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                                class_weight="balanced", random_state=self.seed)
        self.m.fit(X[FEATURES].to_numpy(), y)
        return self

    def score(self, X):
        return self.m.predict_proba(X[FEATURES].to_numpy())[:, 1]


class IsoForest(Detector):
    """Unsupervised: no labels are used for fitting."""

    name = "iforest"
    supervised = False

    def __init__(self, seed: int = 0):
        self.seed = seed

    def fit(self, X, y=None):
        Z = _slog(X[FEATURES].to_numpy())
        self.sc = StandardScaler().fit(Z)
        self.m = IsolationForest(n_estimators=300, random_state=self.seed, n_jobs=1).fit(self.sc.transform(Z))
        return self

    def score(self, X):
        return -self.m.score_samples(self.sc.transform(_slog(X[FEATURES].to_numpy())))


def make_detectors(seed: int = 0) -> list[Detector]:
    return [OTRRule(), IsoForest(seed), Logistic(), GBM(seed)]


# -- evaluation ------------------------------------------------------------
def operating_threshold(det: Detector, train: pd.DataFrame, fpr: float = 0.01) -> float:
    """Score threshold giving `fpr` false positives on the training windows.

    Supervised/rule detectors use training negatives. The unsupervised detector
    has no labels, so it uses the quantile of all training windows.
    """
    s = det.score(train)
    pool = s if not det.supervised and det.name != "otr_rule" else s[train.y.to_numpy() == 0]
    return float(np.quantile(pool, 1 - fpr))


def evaluate(det: Detector, test: pd.DataFrame, thr: float) -> dict:
    s = det.score(test)
    y = test.y.to_numpy()
    flag = s >= thr
    res = {
        "ap": average_precision_score(y, s),
        "recall": flag[y == 1].mean(),
        "fpr": flag[y == 0].mean(),
        "precision": flag[flag].size and (y[flag] == 1).mean(),
    }
    for typ in ("spoof", "pump", "wash"):
        m = (test.type == typ).to_numpy()
        res[f"recall_{typ}"] = flag[m].mean() if m.any() else np.nan
    return res


def false_positive_breakdown(det: Detector, test: pd.DataFrame, thr: float) -> pd.Series:
    """Share of all honest windows of each agent kind that are flagged."""
    s = det.score(test)
    honest = test[test.y == 0].assign(flag=(s >= thr)[test.y.to_numpy() == 0])
    return honest.groupby("kind").flag.mean().sort_values(ascending=False)
