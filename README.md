```markdown
# Análisis del Rendimiento Estudiantil en entornos Virtuales de Aprendizaje (OULAD)

Este repositorio contiene la implementación del proyecto práctico final correspondiente al **Módulo #2 (Ciencias de Datos I - INF-8237-C2)** del programa de Posgrado. El objetivo principal es diseñar un pipeline ETL óptimo para la ingesta de grandes volúmenes de datos académicos y aplicar técnicas analíticas avanzadas para predecir y explicar el rendimiento estudiantil dentro del dataset **Open University Learning Analytics Dataset (OULAD)**.

## 🔗 Enlace del Repositorio
* **URL Oficial:** [https://github.com/rhaynel19/OULAD-Data-Science-Project](https://github.com/rhaynel19/OULAD-Data-Science-Project)

---

## 📁 Estructura del Repositorio

El proyecto se encuentra organizado de forma limpia y modular, excluyendo archivos temporales y datasets masivos de acuerdo con las buenas prácticas de Git:

```text
OULAD-Data-Science-Project/
│
├── DDL.sql                           # Esquema relacional optimizado para bases de datos relacionales.
├── etl_pipeline.py                   # Orquestador ETL estructurado para ingesta masiva por bloques (Chunks).
├── eda_analysis.py                   # Análisis Exploratorio de Datos (EDA) y pruebas estadísticas inferenciales.
├── informe OULAD.docx                # Informe académico y metodológico final del proyecto.
│
└── graficos_paper/                   # Recursos visuales y salidas analíticas generadas por el script
    ├── 1_campana_gauss.png           # Distribución de notas y ajuste a la Normal.
    ├── 2_boxplots_rendimiento.png    # Comparativa de rendimiento entre estudiantes aprobados y reprobados.
    ├── 3_matriz_correlacion.png      # Asociación lineal entre interacciones (VLE) y calificaciones.
    ├── 4_diagrama_dispersion.png     # Tendencia de clústeres y regresión preliminar.
    ├── 5_matriz_confusion.png        # Evaluación de métricas del modelo predictivo.
    ├── pruebas_inferenciales.txt     # Resultados detallados de pruebas de hipótesis (Shapiro-Wilk, T-Student, ANOVA).
    └── tabla_descriptiva_curtosis.csv# Métricas agregadas de asimetría y apuntamiento por cohorte.
