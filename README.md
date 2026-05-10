# Machine Learning — CINF104 (Hospital El Pino, DRG)

Repositorio: [github.com/Rafvtrvs/Machine_Learning](https://github.com/Rafvtrvs/Machine_Learning)

## Estructura del proyecto

```
├── data/                  # Datos brutos (CSV)
│   └── dataset_elpino.csv
├── figures/               # Gráficos generados por el EDA y el modelo
├── results/               # Salidas tabulares (p. ej. classification_report.csv)
├── src/                   # Código principal
│   └── eda_modelo.py
├── notebooks/             # Jupyter / Colab
│   └── EDA (1).ipynb
├── docs/                  # Informe y enunciado
│   ├── paper_ieeeaccess.tex
│   └── CINF104 Proyecto 1 Parte 1 202610.docx
├── requirements.txt
└── README.md
```

## Cómo ejecutar el pipeline

Desde la **raíz** del repositorio (`Trabajo_ML`):

```bash
pip install -r requirements.txt
python -u src/eda_modelo.py
```

El script detecta automáticamente la carpeta del proyecto (padre de `src/`), lee `data/dataset_elpino.csv` y escribe figuras en `figures/` y el reporte en `results/classification_report.csv`.

## LaTeX (IEEE Access)

El archivo `docs/paper_ieeeaccess.tex` usa `\graphicspath{{../figures/}}` para compilar **con el directorio de trabajo en `docs/`**.  

Si en Overleaf subes todo en **una sola carpeta plana**, cambia a `\graphicspath{{./figures/}}` (o mueve el `.tex` a la raíz y ajusta la ruta).

## Nota

Si el repositorio remoto aún aparece vacío, haz `git init`, commit, y `git push` desde esta carpeta para publicar el código y las rutas anteriores.
