"""
============================================================================
MAESTRÍA EN CIENCIA DE DATOS E IA - UASD
DOCUMENTACIÓN DE COLABORACIÓN INTERNA - PROYECTO FINAL ML (COMPLETO)
============================================================================
- Fraimel: Coordinación del motor predictivo, diseño metodológico de las 
  hipótesis de contraste y desarrollo matemático del cálculo manual de F1.
- Edwin: Arquitectura de integración relacional de los libros del Kongo y 
  mapeo de variables macro/micro para los regresores de intervalo-razón.
- Jharol: Orquestación de las mallas de algoritmos supervisados, generación 
  de gráficos del paper (Scatter plots, matrices de confusión) e importancias.
============================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from scipy.stats import kurtosis, skew
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, mean_squared_error, r2_score, confusion_matrix)

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN 
# ============================================================================
DB_USER = "root"
DB_PASS = "8095224147Gael"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "oulad_db"

def obtener_conexion():
    conexion_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conexion_string)


# ============================================================================
# CLASE 1: PROCESADOR DEL EXPERIMENTO (KONGO)
# ============================================================================
class KongoDataProcessor:
    """
    Componente POO especializado en las fases OBTAIN y SCRUB del experimento de contraste.
    Unifica las colecciones indexadas (TAD) aplicando limpieza estricta e imputación.
    """
    def __init__(self, ruta_estudiantes, ruta_clics, ruta_notas):
        self.ruta_estudiantes = ruta_estudiantes
        self.ruta_clics = ruta_clics
        self.ruta_notas = ruta_notas
        self.df_consolidado = None

    def procesar_experimento(self) -> pd.DataFrame:
        print("\n=== [Fase O-S: Kongo] Cargando libros del experimento ===")
        df_stud = pd.read_csv(self.ruta_estudiantes)
        df_clic = pd.read_csv(self.ruta_clics)
        df_nota = pd.read_csv(self.ruta_notas)

        print("[Fase O-S: Kongo] Verificando e igualando nombres de columnas para robustez...")
        id_col_stud = 'guid_student_id' if 'guid_student_id' in df_stud.columns else 'id_student'
        id_col_clic = 'guid_student_id' if 'guid_student_id' in df_clic.columns else 'id_student'
        id_col_nota = 'guid_student_id' if 'guid_student_id' in df_nota.columns else 'id_student'

        print("[Fase O-S: Kongo] Homologando tipos de datos de las llaves (Casteo a str)...")
        df_stud[id_col_stud] = df_stud[id_col_stud].astype(str).str.strip()
        df_clic[id_col_clic] = df_clic[id_col_clic].astype(str).str.strip()
        df_nota[id_col_nota] = df_nota[id_col_nota].astype(str).str.strip()

        print("[Fase O-S: Kongo] Aplicando agregación de interacciones y notas...")
        clicks_agregados = df_clic.groupby(id_col_clic, as_index=False)['sum_clics'].sum()

        score_col = 'score' if 'score' in df_nota.columns else [c for c in df_nota.columns if 'score' in c.lower() or 'nota' in c.lower()][0]
        df_nota[score_col] = pd.to_numeric(df_nota[score_col].replace('?', np.nan), errors='coerce')
        notas_agregadas = df_nota.groupby(id_col_nota, as_index=False)[score_col].mean()

        print("[Fase O-S: Kongo] Enlazando colecciones relacionales (Left Join)...")
        self.df_consolidado = pd.merge(df_stud, clicks_agregados, left_on=id_col_stud, right_on=id_col_clic, how='left')
        self.df_consolidado = pd.merge(self.df_consolidado, notas_agregadas, left_on=id_col_stud, right_on=id_col_nota, how='left')

        self.df_consolidado['sum_clics'] = self.df_consolidado['sum_clics'].fillna(0)
        self.df_consolidado[score_col] = self.df_consolidado[score_col].fillna(0)

        gender_col = 'gender' if 'gender' in self.df_consolidado.columns else 'gender_ordinal'
        if gender_col in self.df_consolidado.columns and self.df_consolidado[gender_col].dtype == object:
            self.df_consolidado['gender_ordinal'] = self.df_consolidado[gender_col].map({'F': 0, 'M': 1}).fillna(0).astype(int)
        elif 'gender_ordinal' not in self.df_consolidado.columns:
            self.df_consolidado['gender_ordinal'] = 0

        self.df_consolidado['target_binario'] = np.where(self.df_consolidado[score_col] >= 40, 1, 0)
        self.df_consolidado.rename(columns={score_col: 'score'}, inplace=True)

        print(f"-> Experimento del Kongo procesado con éxito. Matriz final: {self.df_consolidado.shape}")
        return self.df_consolidado


# ============================================================================
# CLASE 2: MOTOR PREDICTIVO DE MACHINE LEARNING
# ============================================================================
class OULAD_Predictive_Engine:
    """
    Componente maestro bajo POO encargado de las fases de Modelado [M] e Interpretación [I]
    del Proyecto Final de Machine Learning, integrando el experimento de contraste del Kongo.
    """
    def __init__(self):
        self.engine = obtener_conexion()
        self.oulad_df = None
        self.congo_df = None
        self.resultados_metricas = {}

    def cargar_datos_base(self):
        """[O]btain & [S]crub: Extrae tablas de MySQL y delega la agregación masiva a Pandas en RAM"""
        print("\n=== [Fase O-S: OULAD] Extrayendo tablas crudas desde MySQL ===")
        df_si = pd.read_sql("SELECT id_student, gender_ordinal, final_result_ordinal FROM student_info", self.engine)
        df_sa = pd.read_sql("SELECT id_student, score FROM student_assessment", self.engine)
        df_sv = pd.read_sql("SELECT id_student, sum_click FROM student_vle", self.engine)
        
        print("\n=== [Fase S: OULAD] Procesando agregación masiva en memoria RAM con Pandas ===")
        clicks_agregados = df_sv.groupby('id_student', as_index=False)['sum_click'].sum().rename(columns={'sum_click': 'total_clicks'})
        
        df_sa['score'] = pd.to_numeric(df_sa['score'], errors='coerce')
        notas_agregadas = df_sa.groupby('id_student', as_index=False)['score'].mean().rename(columns={'score': 'avg_score'})
        
        print("   -> Consolidando Matriz Analítica Final (Múltiple Left Join)...")
        self.oulad_df = pd.merge(df_si, clicks_agregados, on='id_student', how='left')
        self.oulad_df = pd.merge(self.oulad_df, notas_agregadas, on='id_student', how='left')
        
        self.oulad_df['total_clicks'] = self.oulad_df['total_clicks'].fillna(0)
        self.oulad_df['avg_score'] = self.oulad_df['avg_score'].fillna(0)
        self.oulad_df['target_binario'] = self.oulad_df['final_result_ordinal'].apply(lambda x: 1 if x >= 2 else 0)
        
        print(f"-> Datos base de OULAD consolidados en RAM con éxito. Filas finales: {self.oulad_df.shape[0]}")

    def ejecutar_eda_alto_nivel(self):
        """[E]xplore: Requerimiento obligatorio de EDA Avanzado solicitado por la rúbrica"""
        print("\n=== [Fase E] Ejecutando EDA de Alto Nivel y Cálculo de Curtosis ===")
        
        # 1. Análisis Descriptivo Numérico y Curtosis/Asimetría
        for col in ['total_clicks', 'avg_score']:
            kurt = kurtosis(self.oulad_df[col], fisher=True)
            asimetria = skew(self.oulad_df[col])
            print(f"   -> Métrica '{col}': Curtosis (Fisher) = {kurt:.4f} | Asimetría = {asimetria:.4f}")
        
        # 2. Gráfico Univariado: Histograma de Distribución de Notas
        plt.figure(figsize=(6, 4))
        sns.histplot(self.oulad_df['avg_score'], bins=30, kde=True, color='teal')
        plt.title('EDA: Distribución Univariada de Calificaciones (OULAD)')
        plt.xlabel('Calificación Promedio')
        plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig('graficos_paper/eda_univariado_distribucion.png')
        plt.close()

        # 3. Gráfico Bivariado: Boxplot de Clics agrupados por Target Binario (Tratamiento de Outliers)
        plt.figure(figsize=(6, 4))
        sns.boxplot(x='target_binario', y='total_clicks', data=self.oulad_df, palette='Set2')
        plt.yscale('log') # Escala logarítmica por la alta dispersión de los clics
        plt.title('EDA Bivariado: Boxplot de Interacciones VLE vs Éxito Académico')
        plt.xlabel('Éxito Académico (0=Riesgo, 1=Aprobado)')
        plt.ylabel('Total Clics (Escala Log)')
        plt.tight_layout()
        plt.savefig('graficos_paper/eda_boxplot_outliers.png')
        plt.close()

        # 4. Matriz de Correlación / Heatmap Lineal
        plt.figure(figsize=(5, 4))
        matriz_corr = self.oulad_df[['gender_ordinal', 'total_clicks', 'avg_score', 'target_binario']].corr()
        sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', fmt=".3f", vmin=-1, vmax=1)
        plt.title('EDA Correlacional: Matriz de Coeficientes')
        plt.tight_layout()
        plt.savefig('graficos_paper/eda_heatmap_correlacion.png')
        plt.close()
        print("[EDA] Gráficos avanzados guardados exitosamente en la carpeta 'graficos_paper/'.")

    def calcular_f1_manual(self, y_true, y_pred):
        """Cálculo aritmético manual paso por paso exigido en la rúbrica"""
        y_t = np.array(y_true)
        y_p = np.array(y_pred)
        
        tp = np.sum((y_t == 1) & (y_p == 1))
        fp = np.sum((y_t == 0) & (y_p == 1))
        fn = np.sum((y_t == 1) & (y_p == 0))
        tn = np.sum((y_t == 0) & (y_p == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_calc = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return tp, fp, tn, fn, f1_calc

    def ejecutar_modelos(self, df_kongo):
        """[M]odel & [I]nterpret: Entrena, contrasta y evalúa las variables influyentes"""
        self.congo_df = df_kongo
        
        features = ['gender_ordinal', 'total_clicks', 'avg_score']
        X = self.oulad_df[features]
        y_bin = self.oulad_df['target_binario']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.3, random_state=42)
        
        print("\n=== [Fase M] Entrenando 3 Algoritmos Supervisados (Dicotómicos) ===")
        log_reg = LogisticRegression()
        log_reg.fit(X_train, y_train)
        
        dec_tree = DecisionTreeClassifier(max_depth=5, random_state=42)
        dec_tree.fit(X_train, y_train)
        
        rf_class = RandomForestClassifier(random_state=42)
        rf_class.fit(X_train, y_train)
        
        y_pred_bin = rf_class.predict(X_test)
        y_prob_bin = rf_class.predict_proba(X_test)[:, 1]
        
        tp, fp, tn, fn, f1_manual = self.calcular_f1_manual(y_test, y_pred_bin)
        
        self.resultados_metricas.update({
            'precision_macro': precision_score(y_test, y_pred_bin, average='macro'),
            'recall_macro': recall_score(y_test, y_pred_bin, average='macro'),
            'f1_macro': f1_score(y_test, y_pred_bin, average='macro'),
            'accuracy': accuracy_score(y_test, y_pred_bin),
            'roc_auc': roc_auc_score(y_test, y_prob_bin),
            'f1_score_calculado_manual': f1_manual
        })

        cm = confusion_matrix(y_test, y_pred_bin)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Matriz de Confusión - Random Forest')
        plt.ylabel('Real')
        plt.xlabel('Predicho')
        plt.tight_layout()
        plt.savefig('graficos_paper/confusion_matrix_final.png')
        plt.close()

        print("\n=== [Fase M] Entrenando Regresor para Variable de Intervalo Razón ===")
        y_reg = self.oulad_df['avg_score']
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, y_reg, test_size=0.3, random_state=42)
        
        rf_reg = RandomForestRegressor(random_state=42)
        rf_reg.fit(X_train_r, y_train_r)
        y_pred_reg = rf_reg.predict(X_test_r)
        
        self.resultados_metricas['mse'] = mean_squared_error(y_test_r, y_pred_reg)
        self.resultados_metricas['r2'] = r2_score(y_test_r, y_pred_reg)

        print("\n=== [Fase M] Evaluando Contraste sobre el Experimento Internacional (Kongo) ===")
        X_kongo = self.congo_df[['gender_ordinal', 'sum_clics', 'score']].rename(
            columns={'sum_clics': 'total_clicks', 'score': 'avg_score'}
        )
        y_kongo_real = self.congo_df['score']
        y_kongo_pred = rf_reg.predict(X_kongo)
        
        self.resultados_metricas['msePI2'] = mean_squared_error(y_kongo_real, y_kongo_pred)
        self.resultados_metricas['r2PI2'] = r2_score(y_kongo_real, y_kongo_pred)

        plt.figure(figsize=(6, 4))
        plt.scatter(y_kongo_real, y_kongo_pred, alpha=0.4, color='darkorange')
        plt.title('Scatter Plot: Notas Reales vs Predichos (Validación Kongo)')
        plt.xlabel('Calificación Real (Kongo)')
        plt.ylabel('Calificación Predicha')
        plt.tight_layout()
        plt.savefig('graficos_paper/scatter_plot_kongo.png')
        plt.close()

        print("\n=== [Fase N: Interpretación] Extrayendo Importancia de las Variables ===")
        importancias = rf_class.feature_importances_
        for feat, imp in zip(features, importancias):
            print(f"   -> Variable '{feat}': Importancia Relativa = {imp:.4f}")

        print("\n==========================================")
        print("=== REPORTE CONSOLIDADO DE MÉTRICAS ===")
        print("==========================================")
        for metrica, valor in self.resultados_metricas.items():
            print(f"{metrica:<27}: {valor:.4f}")
        print(f"Componentes Manuales Matriz -> TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")

        # Solución de Faltante: Dataset Caso a Caso Completo (Clasificación + Regresión)
        df_salida = pd.DataFrame({
            'y_test_real_dicotomico': y_test.values,
            'y_pred_dicotomico': y_pred_bin,
            'y_test_real_regresion': y_test_r.values,
            'y_pred_regresion': y_pred_reg
        }).reset_index(drop=True)
        df_salida.to_csv('predictive_models_general.csv', index=False)
        print("\n[Salida] Archivo 'predictive_models_general.csv' unificado y generado con éxito.")


# ============================================================================
# CONTROLADOR PRINCIPAL DE EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    os.makedirs("graficos_paper", exist_ok=True)
    
    procesador = KongoDataProcessor(
        ruta_estudiantes='studentInfo.csv',      
        ruta_clics='VLE_clickStream.csv',       
        ruta_notas='studentAssessment.csv'      
    )
    df_kongo_limpio = procesador.procesar_experimento()
    
    motor = OULAD_Predictive_Engine()
    motor.cargar_datos_base()
    motor.ejecutar_eda_alto_nivel() # Inyección del EDA Automatizado
    motor.ejecutar_modelos(df_kongo_limpio)