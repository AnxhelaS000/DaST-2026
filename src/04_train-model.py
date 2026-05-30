"""Frost Day Prediction – Model Training Pipeline.

CRISP-DM pipeline that loads data from DBRepo, trains a Random Forest
Classifier, evaluates it, and saves all output artefacts.

Outputs (written to outputs/):
    model_random-forest_v1.joblib     Trained model
    fig_confusion-matrix_<date>.png   Confusion matrix
    fig_roc-curve_<date>.png          ROC-AUC curve
    fig_feature-importance_<date>.png Feature importance chart
    metrics_<date>.csv                Evaluation metrics
"""

from __future__ import annotations

import sys
import importlib.util
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
)

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR   = REPO_ROOT / "src"
OUT_DIR   = REPO_ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TODAY = date.today().isoformat()

# ── Load data from DBRepo ────────────────────────────────────────────────────
def _load_dbrepo_module():
    spec = importlib.util.spec_from_file_location(
        "dbrepo_loader",
        SRC_DIR / "02_load-data-from-dbrepo.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


print("Loading data from DBRepo …")
loader = _load_dbrepo_module()
X, y = loader.load_frost_day_data()
print(f"  Rows    : {len(X)}")
print(f"  Features: {list(X.columns)}")
print(f"  Frost days: {y.sum()} / {len(y)}")

# ── Train / Validation / Test split  (70 / 15 / 15) ─────────────────────────
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
)
print(f"\nSplit — train: {len(X_train)}  val: {len(X_val)}  test: {len(X_test)}")

# ── Scaling ──────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s   = scaler.transform(X_val)
X_test_s  = scaler.transform(X_test)

# ── Hyperparameter search via 5-fold CV on training set ─────────────────────
print("\nTuning hyperparameters …")
best_params = {"n_estimators": 100, "max_depth": None}
best_score  = -1.0

for n_est in [100, 200]:
    for max_d in [None, 10, 20]:
        clf = RandomForestClassifier(
            n_estimators=n_est, max_depth=max_d,
            random_state=42, n_jobs=-1,
        )
        cv_scores = cross_val_score(
            clf, X_train_s, y_train,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="f1",
        )
        mean_f1 = cv_scores.mean()
        print(f"  n_estimators={n_est}  max_depth={max_d}  → F1={mean_f1:.4f}")
        if mean_f1 > best_score:
            best_score  = mean_f1
            best_params = {"n_estimators": n_est, "max_depth": max_d}

print(f"\nBest params: {best_params}  (CV F1={best_score:.4f})")

# ── Final model ──────────────────────────────────────────────────────────────
model = RandomForestClassifier(**best_params, random_state=42, n_jobs=-1)
model.fit(X_train_s, y_train)

# ── Evaluation on test set ───────────────────────────────────────────────────
y_pred      = model.predict(X_test_s)
y_prob      = model.predict_proba(X_test_s)[:, 1]

metrics = {
    "accuracy" : accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred),
    "recall"   : recall_score(y_test, y_pred),
    "f1"       : f1_score(y_test, y_pred),
    "roc_auc"  : roc_auc_score(y_test, y_prob),
    "n_estimators": best_params["n_estimators"],
    "max_depth"   : str(best_params["max_depth"]),
    "train_rows"  : len(X_train),
    "test_rows"   : len(X_test),
}

print("\n── Test-set metrics ──────────────────────────────────")
for k, v in metrics.items():
    print(f"  {k}: {v}")

# ── Save metrics CSV ─────────────────────────────────────────────────────────
metrics_path = OUT_DIR / f"metrics_{TODAY}.csv"
pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
print(f"\nSaved metrics → {metrics_path}")

# ── Confusion matrix ─────────────────────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["No frost", "Frost"],
            yticklabels=["No frost", "Frost"])
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
ax.set_title("Confusion Matrix – Frost Day Prediction")
fig.tight_layout()
cm_path = OUT_DIR / f"fig_confusion-matrix_{TODAY}.png"
fig.savefig(cm_path, dpi=150)
plt.close(fig)
print(f"Saved confusion matrix → {cm_path}")

# ── ROC curve ────────────────────────────────────────────────────────────────
fpr, tpr, _ = roc_curve(y_test, y_prob)
fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(fpr, tpr, label=f"ROC-AUC = {metrics['roc_auc']:.3f}")
ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve – Frost Day Prediction")
ax.legend(loc="lower right")
fig.tight_layout()
roc_path = OUT_DIR / f"fig_roc-curve_{TODAY}.png"
fig.savefig(roc_path, dpi=150)
plt.close(fig)
print(f"Saved ROC curve → {roc_path}")

# ── Feature importance ───────────────────────────────────────────────────────
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values()
fig, ax = plt.subplots(figsize=(6, 4))
importances.plot.barh(ax=ax, color="steelblue")
ax.set_xlabel("Mean decrease in impurity")
ax.set_title("Feature Importance – Random Forest")
fig.tight_layout()
fi_path = OUT_DIR / f"fig_feature-importance_{TODAY}.png"
fig.savefig(fi_path, dpi=150)
plt.close(fig)
print(f"Saved feature importance → {fi_path}")

# ── Save model ───────────────────────────────────────────────────────────────
model_path = OUT_DIR / "model_random-forest_v1.joblib"
joblib.dump({"model": model, "scaler": scaler, "features": list(X.columns)}, model_path)
print(f"Saved model → {model_path}")

print("\nDone.")

 