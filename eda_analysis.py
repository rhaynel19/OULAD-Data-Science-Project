





import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN - FRAIMEL
# ============================================================================
DB_USER = "root"
DB_PASS = "8095224147Gael"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "oulad_db"

def obtener_conexion():
    conexion_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conexion_string)

def generar_eda_extendido():
    print("=== INICIANDO ANÁLISIS EXPLORATORIO DE DATOS (EDA EXTENDIDO) ===")
    engine = obtener_conexion()
    
    # Crear carpeta para almacenar los gráficos del artículo
    os.makedirs("graficos_paper", exist_ok=True)
    
    # ------------------------------------------------------------------------
    # 1. EXTRACCIÓN DE DATOS INTEGRADOS
    # ------------------------------------------------------------------------
    print("\n[1] Extrayendo datos desde MySQL...")
    query = """
        SELECT 
            si.id_student, si.gender_ordinal, si.education_ordinal, 
            si.age_ordinal, si.disability_ordinal, si.final_result_ordinal, si.final_result,
            COALESCE(vle.total_clicks, 0) as total_clicks,
            COALESCE(assess.avg_score, 0) as avg_score
        FROM student_info si
        LEFT JOIN (
            SELECT id_student, SUM(sum_click) as total_clicks 
            FROM student_vle 
            GROUP BY id_student
        ) vle ON si.id_student = vle.id_student
        LEFT JOIN (
            SELECT id_student, AVG(score) as avg_score 
            FROM student_assessment 
            GROUP BY id_student
        ) assess ON si.id_student = assess.id_student;
    """
    df = pd.read_sql(query, con=engine)
    
    # ------------------------------------------------------------------------
    # 2. ESTADÍSTICA DESCRIPTIVA, CURTOSIS Y ASIMETRÍA
    # ------------------------------------------------------------------------
    print("\n[2] Calculando Métricas Estadísticas Avanzadas...")
    metricas = ['total_clicks', 'avg_score']
    stats_dict = {}
    
    for col in metricas:
        stats_dict[col] = {
            'Media': df[col].mean(),
            'Mediana': df[col].median(),
            'Desv. Estándar': df[col].std(),
            'Asimetría (Skewness)': df[col].skew(),
            'Curtosis (Kurtosis)': df[col].kurtosis()
        }
    
    df_stats = pd.DataFrame(stats_dict)
    print("\n--- TABLA DE MÉTRICAS (Para la Metodología/Resultados del Paper) ---")
    print(df_stats.round(4))
    df_stats.to_csv("graficos_paper/tabla_descriptiva_curtosis.csv")

    # ------------------------------------------------------------------------
    # 3. CAMPANA DE GAUSS / DISTRIBUCIÓN DE DENSIDAD (KDE)
    # ------------------------------------------------------------------------
    print("\n[3] Generando Gráficos de Distribución (Campana de Gauss)...")
    plt.figure(figsize=(12, 5))
    
    # Distribución de Calificaciones
    plt.subplot(1, 2, 1)
    sns.histplot(df['avg_score'], kde=True, color='darkblue', stat='density')
    plt.title('Distribución Gaussiana Estimada de Calificaciones')
    plt.xlabel('Promedio de Calificación (Score)')
    plt.ylabel('Densidad')
    
    # Distribución de Clics (Aplicando escala logarítmica debido al sesgo extremo)
    plt.subplot(1, 2, 2)
    sns.histplot(df['total_clicks'] + 1, kde=True, color='crimson', stat='density', log_scale=True)
    plt.title('Distribución de Clics en la Plataforma (Escala Log)')
    plt.xlabel('Total de Clics (Log Scale)')
    plt.ylabel('Densidad')
    
    plt.tight_layout()
    plt.savefig("graficos_paper/1_campana_gauss.png", dpi=300)
    plt.close()

    # ------------------------------------------------------------------------
    # 4. DIAGRAMA DE CAJA Y BIGOTES (BOXPLOT)
    # ------------------------------------------------------------------------
    print("[4] Generando Boxplots Comparativos...")
    plt.figure(figsize=(12, 5))
    
    # Boxplot de Notas según el Nivel Educativo previo
    plt.subplot(1, 2, 1)
    sns.boxplot(x='education_ordinal', y='avg_score', data=df, palette='Set2')
    plt.title('Rendimiento por Nivel Educativo Ordinal')
    plt.xlabel('Nivel Educativo (0 a 4)')
    plt.ylabel('Calificación Promedio')
    
    # Boxplot de Clics según Resultado Final
    plt.subplot(1, 2, 2)
    sns.boxplot(x='final_result', y='total_clicks', data=df, palette='Set3')
    plt.yscale('log') # Escala logarítmica para ver bien los cuartiles
    plt.title('Interacciones en VLE según Resultado Final')
    plt.xlabel('Resultado Académico')
    plt.ylabel('Total Clics (Log Scale)')
    
    plt.tight_layout()
    plt.savefig("graficos_paper/2_boxplots_rendimiento.png", dpi=300)
    plt.close()

    # ------------------------------------------------------------------------
    # 5. MATRIZ DE CORRELACIÓN CORRELACIONAL
    # ------------------------------------------------------------------------
    print("[5] Generando Matriz de Correlación...")
    plt.figure(figsize=(8, 6))
    columnas_corr = ['gender_ordinal', 'education_ordinal', 'age_ordinal', 
                     'disability_ordinal', 'total_clicks', 'avg_score', 'final_result_ordinal']
    matriz_corr = df[columnas_corr].corr()
    
    sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', fmt=".3f", linewidths=0.5)
    plt.title('Matriz de Correlación de Pearson')
    plt.tight_layout()
    plt.savefig("graficos_paper/3_matriz_correlacion.png", dpi=300)
    plt.close()

    # ------------------------------------------------------------------------
    # 6. DIAGRAMA DE DISPERSIÓN (SCATTER PLOT)
    # ------------------------------------------------------------------------
    print("[6] Generando Diagrama de Dispersión...")
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='total_clicks', y='avg_score', hue='final_result', data=df, alpha=0.5, palette='deep')
    plt.xscale('log')
    plt.title('Dispersión: Clics en VLE vs Calificación Promedio')
    plt.xlabel('Total de Clics del Estudiante (Log Scale)')
    plt.ylabel('Calificación Promedio')
    plt.legend(title='Resultado Final')
    plt.tight_layout()
    plt.savefig("graficos_paper/4_diagrama_dispersion.png", dpi=300)
    plt.close()

    # ------------------------------------------------------------------------
    # 7. PRUEBAS INFERENCIALES (ANOVA Y T-TEST)
    # ------------------------------------------------------------------------
    print("\n[7] Ejecutando Pruebas Estadísticas Inferenciales...")
    
    # ANOVA: ¿El promedio de clics varía según el resultado final del estudiante?
    grupos_clicks = [df[df['final_result'] == res]['total_clicks'] for res in df['final_result'].unique()]
    f_stat, p_val_anova = stats.f_oneway(*grupos_clicks)
    
    # T-TEST: ¿Hay diferencias significativas en las notas entre alumnos con y sin discapacidad?
    con_discapacidad = df[df['disability_ordinal'] == 1]['avg_score']
    sin_discapacidad = df[df['disability_ordinal'] == 0]['avg_score']
    t_stat, p_val_ttest = stats.ttest_ind(con_discapacidad, sin_discapacidad, equal_var=False)
    
    print(f"   -> ANOVA de Clics vs Resultado: F-Statistic = {f_stat:.4f}, p-value = {p_val_anova}")
    print(f"   -> T-Test de Notas vs Discapacidad: T-Statistic = {t_stat:.4f}, p-value = {p_val_ttest}")
    
    # Guardar resultados de pruebas en texto para el paper
    with open("graficos_paper/pruebas_inferenciales.txt", "w") as f:
        f.write(f"Resultados de Pruebas Hipoteticas (Formato APA):\n")
        f.write(f"ANOVA F({len(grupos_clicks)-1}, {len(df)-len(grupos_clicks)}) = {f_stat:.2f}, p = {p_val_anova}\n")
        f.write(f"T-Test t({len(con_discapacidad)+len(sin_discapacidad)-2:.0f}) = {t_stat:.2f}, p = {p_val_ttest}\n")

    # ------------------------------------------------------------------------
    # 8. MATRIZ DE CONFUSIÓN (MODELO PROTOTIPO DE ANALÍTICA PREDICTIVA)
    # ------------------------------------------------------------------------
    print("[8] Generando Matriz de Confusión mediante Clasificador...")
    # Variable objetivo binaria: Éxito (Pass/Distinction = 1) vs Riesgo (Fail/Withdrawn = 0)
    df['exito_academico'] = df['final_result_ordinal'].apply(lambda x: 1 if x >= 2 else 0)
    
    X = df[['gender_ordinal', 'education_ordinal', 'age_ordinal', 'disability_ordinal', 'total_clicks', 'avg_score']]
    y = df['exito_academico']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    modelo = RandomForestClassifier(random_state=42, n_estimators=100)
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=['Riesgo (0)', 'Éxito (1)'], 
                yticklabels=['Riesgo (0)', 'Éxito (1)'])
    plt.title('Matriz de Confusión: Predicción de Éxito Académico')
    plt.xlabel('Predicción del Modelo')
    plt.ylabel('Clase Real (Histórica)')
    plt.tight_layout()
    plt.savefig("graficos_paper/5_matriz_confusion.png", dpi=300)
    plt.close()
    
    print("\n=== ¡EDA EXTENDIDO FINALIZADO CON ÉXITO! ===")
    print("Todos los insumos visuales y numéricos se guardaron en la carpeta: 'graficos_paper'")

if __name__ == "__main__":
    generar_eda_extendido()