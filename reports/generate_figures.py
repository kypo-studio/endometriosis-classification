"""Script pour régénérer les figures du rapport."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sns.set_theme(style="whitegrid", palette="viridis")

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
RANDOM_STATE = 42

df = pd.read_csv(Path(__file__).parent.parent / "data" / "structured_endometriosis_data.csv")

# 1. Target distribution
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
sns.countplot(x="Diagnosis", data=df, ax=ax[0], palette="viridis")
ax[0].set_title("Répartition du diagnostic")
ax[0].set_xticklabels(["Pas d'endométriose", "Endométriose"])
counts = df["Diagnosis"].value_counts()
ax[1].pie(counts, labels=["Pas d'endométriose", "Endométriose"],
          autopct="%1.1f%%", colors=sns.color_palette("viridis", 2))
ax[1].set_title("Proportion du diagnostic")
plt.tight_layout()
plt.savefig(OUT / "01_target_distribution.png", dpi=120, bbox_inches="tight")
plt.close()

# 2. Numerical distributions
numerical = ["Age", "Chronic_Pain_Level", "BMI"]
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for i, col in enumerate(numerical):
    sns.histplot(df[col], kde=True, ax=axes[i], color=sns.color_palette("viridis")[i])
    axes[i].set_title(f"Distribution - {col}")
plt.tight_layout()
plt.savefig(OUT / "02_numerical_distributions.png", dpi=120, bbox_inches="tight")
plt.close()

# 3. Boxplots by diagnosis
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for i, col in enumerate(numerical):
    sns.boxplot(x="Diagnosis", y=col, data=df, ax=axes[i], palette="viridis")
    axes[i].set_title(f"{col} par diagnostic")
    axes[i].set_xticklabels(["Non", "Oui"])
plt.tight_layout()
plt.savefig(OUT / "03_boxplots_by_diagnosis.png", dpi=120, bbox_inches="tight")
plt.close()

# 4. Binary features vs diagnosis
binary = ["Menstrual_Irregularity", "Hormone_Level_Abnormality", "Infertility"]
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for i, col in enumerate(binary):
    ct = pd.crosstab(df[col], df["Diagnosis"], normalize="index") * 100
    ct.plot(kind="bar", stacked=True, ax=axes[i], color=sns.color_palette("viridis", 2))
    axes[i].set_title(f"Diagnostic selon {col}")
    axes[i].set_ylabel("%")
    axes[i].legend(["Non", "Oui"], title="Diagnostic")
    axes[i].set_xticklabels(["Non", "Oui"], rotation=0)
plt.tight_layout()
plt.savefig(OUT / "04_binary_vs_diagnosis.png", dpi=120, bbox_inches="tight")
plt.close()

# 5. Correlation matrix
plt.figure(figsize=(8, 6))
sns.heatmap(df.corr(), annot=True, cmap="viridis", fmt=".2f", linewidths=0.5, center=0)
plt.title("Matrice de corrélation")
plt.tight_layout()
plt.savefig(OUT / "05_correlation_matrix.png", dpi=120, bbox_inches="tight")
plt.close()

# 6. Target correlation bar
target_corr = df.corr()["Diagnosis"].drop("Diagnosis").sort_values(ascending=False)
plt.figure(figsize=(8, 4))
sns.barplot(x=target_corr.values, y=target_corr.index, palette="viridis")
plt.title("Corrélation des variables avec Diagnosis")
plt.xlabel("Coefficient")
plt.axvline(0, color="black", linestyle="--", linewidth=1)
plt.tight_layout()
plt.savefig(OUT / "06_target_correlations.png", dpi=120, bbox_inches="tight")
plt.close()

# === Modeling ===
X = df.drop(columns=["Diagnosis"])
y = df["Diagnosis"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

models = {
    "Logistic Regression": Pipeline([
        ("s", StandardScaler()),
        ("c", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
    ]),
    "KNN": Pipeline([("s", StandardScaler()), ("c", KNeighborsClassifier(n_neighbors=7))]),
    "SVM": Pipeline([
        ("s", StandardScaler()),
        ("c", SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=RANDOM_STATE)),
    ]),
    "Random Forest": Pipeline([
        ("s", StandardScaler()),
        ("c", RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                     random_state=RANDOM_STATE, n_jobs=-1)),
    ]),
    "Gradient Boosting": Pipeline([
        ("s", StandardScaler()),
        ("c", GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE)),
    ]),
}

# Cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_results = {}
for name, pipe in models.items():
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)
    cv_results[name] = scores

cv_df = pd.DataFrame(cv_results)
plt.figure(figsize=(10, 5))
sns.boxplot(data=cv_df, palette="viridis")
plt.title("F1-score - Validation croisée 5-fold")
plt.ylabel("F1-score")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT / "07_cv_f1_scores.png", dpi=120, bbox_inches="tight")
plt.close()

# Fit and evaluate
results = []
trained = {}
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    trained[name] = pipe
    yp = pipe.predict(X_test)
    ypr = pipe.predict_proba(X_test)[:, 1]
    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, yp),
        "Precision": precision_score(y_test, yp),
        "Recall": recall_score(y_test, yp),
        "F1": f1_score(y_test, yp),
        "ROC-AUC": roc_auc_score(y_test, ypr),
    })

results_df = pd.DataFrame(results).set_index("Model").round(4)
results_df.to_csv(OUT.parent / "model_results.csv")
print(results_df)

# Metric comparison
fig, ax = plt.subplots(figsize=(12, 5))
results_df.plot(kind="bar", ax=ax, colormap="viridis")
ax.set_title("Comparaison des métriques par modèle")
ax.set_ylabel("Score")
ax.set_ylim(0, 1)
ax.legend(loc="lower right")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT / "08_metric_comparison.png", dpi=120, bbox_inches="tight")
plt.close()

# ROC curves
plt.figure(figsize=(8, 7))
colors = sns.color_palette("viridis", len(trained))
for (name, pipe), color in zip(trained.items(), colors):
    ypr = pipe.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, ypr)
    auc = roc_auc_score(y_test, ypr)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=color, linewidth=2)
plt.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Aléatoire")
plt.xlabel("Taux de faux positifs")
plt.ylabel("Taux de vrais positifs")
plt.title("Courbes ROC")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(OUT / "09_roc_curves.png", dpi=120, bbox_inches="tight")
plt.close()

# Confusion matrices
fig, axes = plt.subplots(1, 5, figsize=(20, 4))
for ax, (name, pipe) in zip(axes, trained.items()):
    cm = confusion_matrix(y_test, pipe.predict(X_test))
    ConfusionMatrixDisplay(cm, display_labels=["Non", "Oui"]).plot(
        ax=ax, cmap="viridis", colorbar=False
    )
    ax.set_title(name)
plt.tight_layout()
plt.savefig(OUT / "10_confusion_matrices.png", dpi=120, bbox_inches="tight")
plt.close()

# Feature importance (tree models)
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, name in zip(axes, ["Random Forest", "Gradient Boosting"]):
    clf = trained[name].named_steps["c"]
    imp = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=True)
    sns.barplot(x=imp.values, y=imp.index, ax=ax, palette="viridis")
    ax.set_title(f"Importance des variables - {name}")
plt.tight_layout()
plt.savefig(OUT / "11_feature_importance.png", dpi=120, bbox_inches="tight")
plt.close()

print(f"\n{len(list(OUT.glob('*.png')))} figures générées dans {OUT}")
