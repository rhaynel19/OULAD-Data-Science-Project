Markdown
# Analítica de Aprendizaje y Modelado Predictivo de Deserción Estudiantil (OULAD & RDC)

Este repositorio contiene la implementación del proyecto práctico de fin de módulo correspondiente a **Ciencias de Datos I (INF-8237-C2)** dentro del programa de Posgrado de la **Universidad Autónoma de Santo Domingo (UASD)**. 

El objetivo principal es diseñar un ecosistema analítico modular en Python bajo el paradigma de **Programación Orientada a Objetos (POO)** y el flujo metodológico **OSEMN**, orientado a la detección temprana del riesgo de abandono y la predicción del rendimiento continuo de los estudiantes.

## 🔗 Enlace Oficial del Repositorio
* **URL:** [https://github.com/rhaynel19/OULAD-Data-Science-Project](https://github.com/rhaynel19/OULAD-Data-Science-Project)

---

## 📁 Estructura del Ecosistema Analítico

El proyecto se encuentra organizado de forma limpia y modular, excluyendo datasets masivos mediante reglas estrictas de control de versiones (`.gitignore`):

```text
OULAD-Data-Science-Project/
│
├── DDL.sql                           # Esquema relacional e indexación optimizada en MySQL.
├── etl_pipeline.py                   # Orquestador del pipeline de datos (Ingesta, Limpieza y Mapeo).
├── eda_analysis.py                   # Automatización del Análisis Exploratorio de Datos y estadística inferencial.
├── ml_modeling.py                    # Pipeline de Machine Learning (Modelado predictivo y regresión transnacional).
├── .gitignore                        # Exclusión de entornos virtuales (.venv) y archivos CSV/XLSX de gran tamaño.
│
└── graficos_paper/                   # Recursos visuales y salidas analíticas oficiales del modelo
    ├── eda_univariado_distribucion.png # Distribución de notas y sesgo de la densidad.
    ├── eda_boxplot_outliers.png       # Dispersión y outliers de interacciones VLE según éxito académico.
    ├── eda_heatmap_correlacion.png    # Matriz de coeficientes lineales entre variables.
    ├── confusion_matrix_final.png     # Matriz térmica de evaluación del clasificador Random Forest.
    └── scatter_plot_kongo.png         # Gráfico de dispersión del experimento de validación transnacional.
⚙️ Arquitectura del Sistema (Flujo OSEMN)
Obtain (Obtención): Carga y lectura estructurada de datos a través de consultas optimizadas, integrando el histórico del Open University Learning Analytics Dataset (OULAD) (32,593 registros) y un dataset externo de validación de la República Democrática del Congo (148 observaciones).

Scrub (Limpieza): Procesamiento de datos mediante imputación condicional con cero en ausencia de entregas/interacciones, conversión de identificadores a cadenas de texto y codificación binaria de variables categóricas.

Explore (Exploración): Análisis descriptivo automatizado. Se identificó una distribución fuertemente leptocúrtica en las interacciones digitales del entorno virtual (total_clicks con curtosis de 18.12 y asimetría de 3.20).

Model (Modelado): Implementación paralela de algoritmos supervisados de clasificación (Regresión Logística, Árboles de Decisión y Random Forest) utilizando partición 70/30 para entrenamiento y validación.

Interpret (Interpretación): Evaluación de la capacidad de generalización del modelo mediante matrices de confusión y análisis de la importancia de los atributos.

📈 Resultados Clave del Modelo
El algoritmo Random Forest Classifier obtuvo el desempeño más óptimo y robusto para la clasificación del riesgo estudiantil:

ROC-AUC: 0.8558

F1-Score (Macro): 0.7653

Precisión (Macro): 0.7651

Recall (Macro): 0.7655

Importancia de las Variables Predictoras
El análisis de contribución a los nodos determinó que el éxito académico se explica casi en su totalidad por dos factores dinámicos:

Interacciones en el Entorno Virtual (VLE): 50.96%

Rendimiento Académico Previo: 48.28%

Factores Demográficos (Género): 0.76% (Carece de significancia estadística en este entorno predictivo).

🚀 Instalación y Ejecución
Clonar el repositorio:

Bash
git clone [https://github.com/rhaynel19/OULAD-Data-Science-Project.git](https://github.com/rhaynel19/OULAD-Data-Science-Project.git)
cd OULAD-Data-Science-Project
Configurar el entorno virtual e instalar dependencias:

Bash
# En Windows (PowerShell)
python -m venv .venv
& .venv\Scripts\Activate.ps1
pip install -r requirements.txt
Ejecución de los módulos:

Para recrear el análisis exploratorio y exportar las estadísticas básicas: python eda_analysis.py

Para entrenar los modelos de clasificación, regresión y generar las gráficas finales: python ml_modeling.py

Investigador: Fraimel Trinidad

Facilitador: Dr. Silverio Del Orbe Abad

UASD - Maestría en Ciencia de Datos e Inteligencia Artificial (2026) ```

🛠️ Pasos rápidos para subirlo desde VS Code:
Una vez guardes el archivo como README.md, ejecuta en tu terminal:

PowerShell

git add README.md
git commit -m "Docs: Añadir README académico estructurado bajo flujo OSEMN"
git push origin main
git add README.md
git commit -m "Docs: Añadir README académico estructurado bajo flujo OSEMN"
git push origin main
