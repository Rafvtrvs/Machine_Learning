# =============================================================================
# GRD Predictor — EDA + Modelo
# Dataset: Hospital El Pino
# =============================================================================

import re
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sin ventanas — guarda directo a PNG
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import scipy.sparse as sp
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, f1_score, accuracy_score, confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# Raíz del repo: carpeta que contiene data/, figures/, results/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "dataset_elpino.csv"
FIG_DIR = PROJECT_ROOT / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"
FIG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MIN_SAMPLES_PER_CLASS = 10   # clases con menos muestras se descartan
RANDOM_STATE = 42

# =============================================================================
# 1. CARGA CORRECTA DEL CSV
# =============================================================================
print("=" * 60)
print("1. CARGANDO DATOS")
print("=" * 60)


#lee el archivo dataset_elpino.csv y lo convierte en un DF (sin modificar, por eso raw)
df_raw = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8", encoding_errors="replace")


#muestra filas(pacientes) y columnas de la tabla
print(f"Filas: {df_raw.shape[0]:,}  |  Columnas: {df_raw.shape[1]}")

# Renombrar columnas para facilitar el trabajo

#identificamos y agrupamos las columnas de diagnóstico y procedimiento mediante listas de comprensión.
diag_cols  = [c for c in df_raw.columns if c.startswith("Diag")]
proced_cols = [c for c in df_raw.columns if c.startswith("Proced")]
age_col  = "Edad en años"
sex_col  = "Sexo (Desc)"
grd_col  = "GRD"

print(f"Columnas diagnóstico : {len(diag_cols)}")
print(f"Columnas procedimiento: {len(proced_cols)}")

# =============================================================================
# 2. EXTRACCIÓN DE CÓDIGOS CIE / ICD
# =============================================================================
print("\n" + "=" * 60)
print("2. EXTRACCIÓN DE CÓDIGOS CIE")
print("=" * 60)

#patron que le dice a python como se ve un código CIE
CODE_RE = re.compile(r"^([A-Z]\d{2}\.?\d*|[0-9]{2}\.[0-9]+|[A-Z]\d{2})", re.IGNORECASE)


#funcion que recibe una celda del CSV y devuelve sólo el código. Maneja tres casos previos (celdas vacías, celdas nan, celdas "-")
def extract_code(cell):
    """Devuelve el código CIE/ICD desde una celda 'CODE - descripción'."""
    if pd.isna(cell):
        return None
    s = str(cell).strip()
    if s in ("-", "", "nan"):
        return None
    m = CODE_RE.match(s)
    return m.group(1).upper() if m else None

# aplica los codigos a todas las columnas de diagnostico y procedimiento.
for col in diag_cols + proced_cols:
    df_raw[col + "_code"] = df_raw[col].apply(extract_code)

# almacenamos los nombres de las columnas _code mediante listas comprensivas  
diag_code_cols   = [c + "_code" for c in diag_cols]
proced_code_cols = [c + "_code" for c in proced_cols]

# extrae en una sola lista los códigos CIE por paciente de diagnóstico y procedimiento.
df_raw["diag_list"]   = df_raw[diag_code_cols].apply(
    lambda row: [v for v in row if pd.notna(v)], axis=1
)
df_raw["proced_list"] = df_raw[proced_code_cols].apply(
    lambda row: [v for v in row if pd.notna(v)], axis=1
)

# Toma todos los codigos y los une en una sola lista. Necesario para el EDA.
df_raw["all_codes"]   = df_raw["diag_list"] + df_raw["proced_list"]

# =============================================================================
# 3. VARIABLES NUMÉRICAS Y CATEGÓRICAS
# =============================================================================
df_raw[age_col] = pd.to_numeric(df_raw[age_col], errors="coerce")
df_raw[sex_col] = df_raw[sex_col].astype(str).str.strip()
df_raw[grd_col] = df_raw[grd_col].astype(str).str.strip()

# Eliminar posibles filas sin GRD o GRD = 'nan'
df_raw = df_raw[df_raw[grd_col].notna() & (df_raw[grd_col] != "nan")].copy()

# Extraer solo el código numérico del GRD (primeros 6 dígitos)
df_raw["grd_code"] = df_raw[grd_col].str.extract(r"^(\d{6})")
df_raw["n_diag"]   = df_raw["diag_list"].apply(len)
df_raw["n_proced"] = df_raw["proced_list"].apply(len)
df_raw["n_total"]  = df_raw["all_codes"].apply(len)

print(f"Pacientes tras limpieza: {len(df_raw):,}")
print(f"Clases GRD únicas      : {df_raw['grd_code'].nunique()}")

# =============================================================================
# 4. EDA — CALIDAD DE DATOS
# =============================================================================
print("\n" + "=" * 60)
print("4. CALIDAD DE DATOS")
print("=" * 60)

# 4.1 Edad
print("\n--- Edad ---")
print(df_raw[age_col].describe().round(1))
outliers_age = df_raw[(df_raw[age_col] < 0) | (df_raw[age_col] > 110)]
print(f"Valores outlier en edad (<0 o >110): {len(outliers_age)}")
print(f"Edad nula (NaN): {df_raw[age_col].isna().sum()}")

# 4.2 Sexo
print("\n--- Sexo ---")
print(df_raw[sex_col].value_counts(dropna=False))

# 4.3 Completitud de diagnósticos
completeness = (df_raw[diag_code_cols].notna().sum(axis=0) / len(df_raw) * 100).round(1)
print("\n--- Completitud por columna de diagnóstico (%) ---")
print(completeness.to_string())

# 4.4 Clases GRD raras
class_counts = df_raw["grd_code"].value_counts()
rare = class_counts[class_counts < MIN_SAMPLES_PER_CLASS]
print(f"\nClases con < {MIN_SAMPLES_PER_CLASS} muestras: {len(rare)} "
      f"({len(rare)/df_raw['grd_code'].nunique()*100:.1f}% de clases, "
      f"{rare.sum()} pacientes)")

# =============================================================================
# 5. EDA — ESTADÍSTICAS DESCRIPTIVAS Y GRÁFICOS
# =============================================================================
print("\n" + "=" * 60)
print("5. VISUALIZACIONES")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Exploratory Data Analysis — Hospital El Pino", fontsize=14, fontweight="bold")

# 5.1 Distribución de edad
axes[0, 0].hist(df_raw[age_col].dropna(), bins=30, color="steelblue", edgecolor="white")
axes[0, 0].set_title("Age Distribution")
axes[0, 0].set_xlabel("Age (years)")
axes[0, 0].set_ylabel("Count")

# 5.2 Distribución de sexo
sex_counts = df_raw[sex_col].value_counts()
axes[0, 1].bar(sex_counts.index, sex_counts.values, color=["steelblue", "salmon"])
axes[0, 1].set_title("Sex Distribution")
axes[0, 1].set_ylabel("Count")

# 5.3 Top 10 GRD
top10_grd = df_raw[grd_col].value_counts().head(10)
axes[0, 2].barh(top10_grd.index[::-1], top10_grd.values[::-1], color="steelblue")
axes[0, 2].set_title("Top 10 GRD Classes")
axes[0, 2].set_xlabel("Count")
axes[0, 2].tick_params(axis="y", labelsize=7)

# 5.4 Número de diagnósticos por paciente
axes[1, 0].hist(df_raw["n_diag"], bins=20, color="teal", edgecolor="white")
axes[1, 0].set_title("Diagnoses per Patient")
axes[1, 0].set_xlabel("Number of diagnoses")
axes[1, 0].set_ylabel("Count")

# 5.5 Número de procedimientos por paciente
axes[1, 1].hist(df_raw["n_proced"], bins=20, color="coral", edgecolor="white")
axes[1, 1].set_title("Procedures per Patient")
axes[1, 1].set_xlabel("Number of procedures")
axes[1, 1].set_ylabel("Count")

# 5.6 Distribución de clases GRD (log scale) — desbalance
sorted_counts = class_counts.values
axes[1, 2].plot(range(len(sorted_counts)), sorted_counts, color="purple")
axes[1, 2].set_yscale("log")
axes[1, 2].set_title("GRD Class Distribution (log scale)")
axes[1, 2].set_xlabel("Class rank")
axes[1, 2].set_ylabel("Samples (log)")

plt.tight_layout()
plt.savefig(FIG_DIR / "eda_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado: eda_overview.png")

# 5.7 Completitud de columnas de diagnóstico
fig2, ax = plt.subplots(figsize=(12, 4))
ax.bar(range(len(completeness)), completeness.values, color="steelblue")
ax.set_xticks(range(len(completeness)))
ax.set_xticklabels([f"D{i+1:02d}" for i in range(len(completeness))], rotation=45)
ax.set_title("Completeness (%) — Diagnosis Columns")
ax.set_ylabel("% Non-null")
ax.axhline(50, color="red", linestyle="--", label="50% threshold")
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_completeness.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado: eda_completeness.png")

# 5.8 Top 15 códigos CIE más frecuentes
all_codes_flat = [c for lst in df_raw["diag_list"] for c in lst if isinstance(c, str)]
top15 = Counter(all_codes_flat).most_common(15)
codes_df = pd.DataFrame(top15, columns=["code", "count"])
codes_df["code"] = codes_df["code"].astype(str)
fig3, ax = plt.subplots(figsize=(12, 5))
ax.barh(codes_df["code"].tolist()[::-1], codes_df["count"].tolist()[::-1], color="steelblue")
ax.set_title("Top 15 Most Frequent Diagnosis Codes (ICD)")
ax.set_xlabel("Frequency")
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_top_codes.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado: eda_top_codes.png")

print("\n--- Top 15 diagnósticos más frecuentes ---")
for code, freq in top15:
    print(f"  {code:10s} -> {freq:5d}")

# =============================================================================
# 6. BALANCEO DE CLASES — FILTRO DE CLASES RARAS
# =============================================================================
print("\n" + "=" * 60)
print("6. BALANCEO DE CLASES")
print("=" * 60)

# Conservar solo clases con >= MIN_SAMPLES_PER_CLASS muestras
valid_classes = class_counts[class_counts >= MIN_SAMPLES_PER_CLASS].index
df = df_raw[df_raw["grd_code"].isin(valid_classes)].copy()

print(f"Pacientes antes del filtro : {len(df_raw):,}")
print(f"Pacientes después del filtro: {len(df):,}")
print(f"Clases antes del filtro    : {df_raw['grd_code'].nunique()}")
print(f"Clases después del filtro  : {df['grd_code'].nunique()}")
print(f"\nNota: class_weight='balanced' se usará en todos los modelos")

# =============================================================================
# 7. PREPARACIÓN DE FEATURES
# =============================================================================
print("\n" + "=" * 60)
print("7. PREPARACIÓN DE FEATURES")
print("=" * 60)

# 7.1 One-hot encoding de códigos (MultiLabelBinarizer) — sparse para eficiencia
mlb_diag   = MultiLabelBinarizer(sparse_output=True)
mlb_proced = MultiLabelBinarizer(sparse_output=True)

X_diag   = mlb_diag.fit_transform(df["diag_list"])
X_proced = mlb_proced.fit_transform(df["proced_list"])

# 7.2 Variables numéricas / categóricas (también en sparse)
age_arr = df[age_col].fillna(df[age_col].median()).values.reshape(-1, 1)
sex_arr = (df[sex_col] == "Hombre").astype(int).values.reshape(-1, 1)
num_sparse = sp.csr_matrix(np.hstack([age_arr, sex_arr]))

# 7.3 Concatenar todo en matriz sparse
X = sp.hstack([X_diag, X_proced, num_sparse], format="csr")

# 7.4 Etiqueta
le = LabelEncoder()
y = le.fit_transform(df["grd_code"])

print(f"Shape de X : {X.shape}")
print(f"Clases en y: {len(le.classes_)}")
print(f"Features diagnóstico  : {X_diag.shape[1]}")
print(f"Features procedimiento: {X_proced.shape[1]}")

# =============================================================================
# 8. SPLIT ESTRATIFICADO
# =============================================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"\nTrain: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")

# =============================================================================
# 9. ENTRENAMIENTO Y COMPARACIÓN DE MODELOS
# =============================================================================
print("\n" + "=" * 60)
print("9. ENTRENAMIENTO DE MODELOS (class_weight='balanced')")
print("=" * 60)

models = {
    "Logistic Regression": LogisticRegression(
        class_weight="balanced", max_iter=200,
        solver="saga", C=0.1, tol=1e-2, random_state=RANDOM_STATE
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100, class_weight="balanced",
        max_depth=15, n_jobs=-1, random_state=RANDOM_STATE,
        oob_score=True, warm_start=True
    ),
}

# =============================================================================
# 9b. CURVA OOB — VISUALIZACIÓN DEL PROCESO DE ENTRENAMIENTO
# =============================================================================
print("\nGenerando curva OOB del Random Forest...")
tree_counts = list(range(5, 101, 5))  # 5, 10, 15, ... 100 árboles
oob_errors  = []

rf_oob = RandomForestClassifier(
    class_weight="balanced", max_depth=15,
    n_jobs=-1, random_state=RANDOM_STATE,
    oob_score=True, warm_start=True
)

for n in tree_counts:
    rf_oob.set_params(n_estimators=n)
    rf_oob.fit(X_train, y_train)
    oob_errors.append(1 - rf_oob.oob_score_)

fig_oob, ax_oob = plt.subplots(figsize=(9, 4))
ax_oob.plot(tree_counts, oob_errors, color="steelblue", linewidth=2, marker="o", markersize=4)
ax_oob.set_title("Random Forest — OOB Error vs Number of Trees", fontsize=12)
ax_oob.set_xlabel("Number of Trees")
ax_oob.set_ylabel("OOB Error (1 - OOB Accuracy)")
ax_oob.axvline(x=100, color="red", linestyle="--", label="Selected: 100 trees")
ax_oob.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "oob_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado: oob_curve.png")

results = {}
for name, model in models.items():
    print(f"\nEntrenando: {name} ...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc   = accuracy_score(y_test, y_pred)
    f1_w  = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_m  = f1_score(y_test, y_pred, average="macro",    zero_division=0)

    results[name] = {"Accuracy": acc, "F1 Weighted": f1_w, "F1 Macro": f1_m}
    print(f"  Accuracy    : {acc:.4f}")
    print(f"  F1 Weighted : {f1_w:.4f}")
    print(f"  F1 Macro    : {f1_m:.4f}")

# =============================================================================
# 10. TABLA COMPARATIVA DE RESULTADOS
# =============================================================================
print("\n" + "=" * 60)
print("10. TABLA COMPARATIVA")
print("=" * 60)

results_df = pd.DataFrame(results).T.round(4)
print(results_df.to_string())

# Gráfico comparativo
fig4, ax = plt.subplots(figsize=(9, 4))
results_df.plot(kind="bar", ax=ax, color=["steelblue", "salmon", "teal"], edgecolor="white")
ax.set_title("Model Comparison — GRD Prediction")
ax.set_ylabel("Score")
ax.set_xticklabels(results_df.index, rotation=15, ha="right")
ax.legend(loc="lower right")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(FIG_DIR / "model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico guardado: model_comparison.png")

# =============================================================================
# 11. MEJOR MODELO — REPORTE DETALLADO
# =============================================================================
best_name = max(results, key=lambda k: results[k]["F1 Weighted"])
best_model = models[best_name]
y_pred_best = best_model.predict(X_test)

print(f"\n{'=' * 60}")
print(f"11. MEJOR MODELO: {best_name}")
print("=" * 60)
print("\nClassification Report (top clases):")
# Mostrar solo top 20 clases por soporte para no saturar la consola
report = classification_report(
    y_test, y_pred_best,
    target_names=le.classes_, zero_division=0, output_dict=True
)
report_df = pd.DataFrame(report).T
report_df = report_df[report_df["support"] > 0].sort_values("support", ascending=False)
print(report_df.head(20).round(3).to_string())

# Guardar reporte completo
report_df.to_csv(RESULTS_DIR / "classification_report.csv")
print("\nReporte completo guardado: classification_report.csv")

print("\n¡Script completado exitosamente!")
