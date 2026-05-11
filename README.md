# Trabajo_ML — Proyecto Machine Learning (Hospital El Pino)

Estructura de carpetas y archivos principales:

## Carpetas

| Carpeta | Contenido |
|--------|-----------|
| **`src/`** | Código Python del estudio: carga del dataset, EDA, entrenamiento de modelos (regresión logística y *random forest*), generación de gráficos y export de resultados. Punto de entrada principal: `eda_modelo.py`. |
| **`data/`** | Datos en bruto usados por el script (p. ej. `dataset_elpino.csv`). Por tamaño o privacidad puede no estar versionado en Git; si no existe, hay que colocar aquí el CSV indicado en el código. |
| **`figures/`** | Figuras generadas por el pipeline (EDA, curvas OOB, diagramas, etc.) y/o exportadas para el informe LaTeX. El script guarda aquí los PNG cuando se ejecuta. |
| **`tables/`** | Capturas o tablas exportadas para el paper (p. ej. `Table_1.png`, `Table_2.png`, `Table_3.png`) — estadísticos descriptivos, comparación de modelos, métricas por clase. |
| **`results/`** | Salidas tabulares del entrenamiento/evaluación (p. ej. `classification_report.csv`). |
| **`Paper/`** | Versión PDF del informe o artículo (p. ej. variante IEEE). |
| **`Chatbot/`** | Proyecto aparte: chatbot fase 2 |
| **`Video/`** | Material de video del proyecto (p. ej. demostración o presentación). |

## Archivos en la raíz

- **`README.md`** — Esta guía de estructura.
- **`.gitattributes`** — Configuración de Git (fines de línea, etc.).


## Enlace del repositorio

Código y evolución del proyecto: [https://github.com/Rafvtrvs/Machine_Learning](https://github.com/Rafvtrvs/Machine_Learning).
