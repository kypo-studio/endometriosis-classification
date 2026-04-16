# Endometriosis Classification

Analyse exploratoire et classification supervisée sur un dataset synthétique d'endométriose, avec comparaison de plusieurs modèles de machine learning.

## Contexte

L'endométriose est une maladie gynécologique chronique qui touche environ 1 femme sur 10 en âge de procréer. Son diagnostic est souvent tardif (plusieurs années en moyenne). Ce projet utilise un jeu de données synthétique réaliste pour explorer les symptômes associés et entraîner des modèles de classification permettant de prédire un diagnostic à partir de variables cliniques simples.

## Dataset

**Source :** [Kaggle - Endometriosis Dataset](https://www.kaggle.com/datasets/michaelanietie/endometriosis-dataset)

- **10 000 observations**, 7 variables
- Données synthétiques mais réalistes, avec des relations logiques entre variables
- Licence : MIT

### Variables

| Variable | Type | Description |
|---|---|---|
| `Age` | int (18-50) | Âge de l'individu |
| `Menstrual_Irregularity` | binaire (0/1) | Irrégularité menstruelle |
| `Chronic_Pain_Level` | float (0-10) | Niveau de douleur chronique |
| `Hormone_Level_Abnormality` | binaire (0/1) | Anomalie des niveaux hormonaux |
| `Infertility` | binaire (0/1) | Infertilité |
| `BMI` | float (15-40) | Indice de masse corporelle |
| `Diagnosis` | binaire (0/1) | **Cible** — présence d'endométriose |

## Structure du projet

```
endometriosis/
├── data/                                      # Dataset brut (gitignored)
│   └── structured_endometriosis_data.csv
├── notebooks/
│   ├── 01_eda.ipynb                           # Analyse exploratoire + visualisations
│   └── 02_modeling.ipynb                      # Entraînement et comparaison des modèles
├── pyproject.toml                             # Dépendances uv
├── uv.lock
└── README.md
```

## Installation

Le projet utilise [uv](https://docs.astral.sh/uv/) pour la gestion des dépendances.

```bash
# Cloner le repo
git clone https://github.com/kypo-studio/endometriosis-classification.git
cd endometriosis-classification

# Installer les dépendances
uv sync
```

## Téléchargement du dataset

Le dataset est téléchargé via l'[API Kaggle](https://github.com/Kaggle/kaggle-api). Assurez-vous d'avoir un fichier `~/.kaggle/kaggle.json` valide, puis :

```bash
uv run kaggle datasets download -d michaelanietie/endometriosis-dataset -p data --unzip
```

## Utilisation

Lancer Jupyter et ouvrir les notebooks :

```bash
uv run jupyter lab
```

1. **`notebooks/01_eda.ipynb`** — Analyse exploratoire : distributions, corrélations, analyses bivariées.
2. **`notebooks/02_modeling.ipynb`** — Pipeline complet d'entraînement et comparaison.

## Modèles comparés

| Modèle | Bibliothèque |
|---|---|
| Logistic Regression | scikit-learn |
| K-Nearest Neighbors | scikit-learn |
| Support Vector Machine (RBF) | scikit-learn |
| Random Forest | scikit-learn |
| Gradient Boosting | scikit-learn |

Chaque modèle est encapsulé dans un `Pipeline` avec `StandardScaler`. Les classes déséquilibrées sont gérées via `class_weight='balanced'` là où c'est disponible.

### Protocole d'évaluation

- Split stratifié 80/20 (`random_state=42`)
- Validation croisée stratifiée 5-fold sur le F1-score
- Métriques sur le test set : Accuracy, Precision, Recall, F1, ROC-AUC

### Résultats (test set)

| Modèle | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.6095 | 0.5172 | 0.6434 | 0.5735 | 0.6575 |
| KNN | 0.5945 | 0.5035 | 0.4363 | 0.4675 | 0.6003 |
| SVM | 0.6075 | 0.5149 | 0.6569 | **0.5773** | 0.6422 |
| Random Forest | 0.6030 | 0.5159 | 0.4375 | 0.4735 | 0.6032 |
| Gradient Boosting | 0.6195 | 0.5518 | 0.3591 | 0.4350 | 0.6380 |

Le **SVM (RBF)** obtient le meilleur F1-score sur le test set, mais la **Logistic Regression** reste très compétitive et plus interprétable.

## Pistes d'amélioration

- Optimisation des hyperparamètres (`GridSearchCV` / `RandomizedSearchCV`)
- Ajustement du seuil de décision pour privilégier le rappel (contexte médical)
- Ajout de modèles boostés (XGBoost, LightGBM, CatBoost)
- Feature engineering (interactions, binning)
- Interprétabilité via SHAP

## Stack technique

- Python 3.12
- uv (gestion des dépendances)
- pandas, numpy
- matplotlib, seaborn
- scikit-learn
- Jupyter

## Licence

MIT — voir le dataset source pour la licence des données.
