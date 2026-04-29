"""
Model Evaluation — confusion matrix, feature importance, ROC curves.

Loads the trained XGBoost model and generates evaluation plots in outputs/plots/.

Usage:
    python evaluate.py
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize

from config import (
    FEATURES_CSV,
    MODEL_PATH,
    PLOTS_DIR,
    FEATURE_COLUMNS,
    LABEL_MAP,
    LABEL_NAMES,
    TEST_SIZE,
    RANDOM_STATE,
)

warnings.filterwarnings("ignore")


def plot_confusion_matrix(y_true, y_pred, class_names, save_path):
    """Normalised confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred, normalize="true")
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Normalised Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  OK: Saved: {save_path}")


def plot_feature_importance(model, feature_names, save_path):
    """Horizontal bar chart of feature importances."""
    importances = model.feature_importances_
    idx = np.argsort(importances)

    plt.figure(figsize=(8, 6))
    plt.barh(range(len(idx)), importances[idx], color="steelblue")
    plt.yticks(range(len(idx)), [feature_names[i] for i in idx])
    plt.xlabel("Importance")
    plt.title("XGBoost Feature Importance")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  OK: Saved: {save_path}")


def plot_roc_curves(y_true, y_prob, class_names, save_path):
    """One-vs-rest ROC curves with AUC scores."""
    n_classes = len(class_names)
    y_bin = label_binarize(y_true, classes=list(range(n_classes)))

    plt.figure(figsize=(8, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, n_classes))

    for i, (name, color) in enumerate(zip(class_names, colors)):
        if y_bin.shape[1] <= i:
            continue
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC={roc_auc:.3f})")

    plt.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
    plt.xlim([0, 1])
    plt.ylim([0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Per-Class ROC Curves (One-vs-Rest)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  OK: Saved: {save_path}")


def main():
    # ── Load model ───────────────────────────────────────────────
    if not os.path.isfile(MODEL_PATH):
        print(f"ERROR: {MODEL_PATH} not found. Run train.py first.")
        sys.exit(1)

    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    print(f"Loaded model from: {MODEL_PATH}")

    # ── Load data & reconstruct same test split ──────────────────
    if not os.path.isfile(FEATURES_CSV):
        print(f"ERROR: {FEATURES_CSV} not found. Run preprocess.py first.")
        sys.exit(1)

    df = pd.read_csv(FEATURES_CSV).dropna()
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values.astype(int)

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # ── Predictions ──────────────────────────────────────────────
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    class_names = [LABEL_NAMES.get(i, str(i)) for i in sorted(LABEL_MAP.values())]

    # ── Metrics ──────────────────────────────────────────────────
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    print(f"\nOverall Accuracy : {acc:.4f}")
    print(f"Macro F1 Score   : {macro_f1:.4f}")

    print("\nPer-Class F1:")
    per_f1 = f1_score(y_test, y_pred, average=None, zero_division=0)
    for name, f in zip(class_names, per_f1):
        print(f"  {name:10s}: {f:.4f}")

    print("\nFull Classification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))

    # ── Generate plots ───────────────────────────────────────────
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("Generating plots...")

    plot_confusion_matrix(
        y_test, y_pred, class_names, os.path.join(PLOTS_DIR, "confusion_matrix.png")
    )
    plot_feature_importance(
        model, FEATURE_COLUMNS, os.path.join(PLOTS_DIR, "feature_importance.png")
    )
    plot_roc_curves(
        y_test, y_prob, class_names, os.path.join(PLOTS_DIR, "roc_curves.png")
    )

    print("\nDONE: Evaluation complete.")


if __name__ == "__main__":
    main()
