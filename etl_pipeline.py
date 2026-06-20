import os
import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================================
# CONFIGURACIÓN DEL ENTORNO Y CONEXIÓN REAL - FRAIMEL
# ============================================================================
DB_USER = "root"
DB_PASS = "8095224147Gael"  # Contraseña validada de tu MySQL local
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "oulad_db"

CSV_DIR = "."

def obtener_conexion():
    """Establece y retorna la conexión al motor de base de datos MySQL."""
    conexion_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conexion_string)
    return engine

# ============================================================================
# FASE DE TRANSFORMACIÓN (CLEANING Y CODIFICACIÓN ORDINAL)
# ============================================================================
def transformar_estudiantes(df_student):
    """Aplica la limpieza y crea las columnas ordinales demográficas."""
    df_student['imd_band'] = df_student['imd_band'].fillna('Missing').str.strip()
    
    map_gender = {'F': 0, 'M': 1}
    df_student['gender_ordinal'] = df_student['gender'].map(map_gender)
    
    map_edu = {
        'No Formal Qualification': 0,
        'Lower Than A Level': 1,
        'A Level': 2,
        'HE Qualification': 3,
        'Post Graduate Qualification': 4
    }
    df_student['education_ordinal'] = df_student['highest_education'].map(map_edu)
    
    map_age = {'0-35': 0, '35-55': 1, '55<=': 2}
    df_student['age_ordinal'] = df_student['age_band'].map(map_age)
    
    map_dis = {'N': 0, 'Y': 1}
    df_student['disability_ordinal'] = df_student['disability'].map(map_dis)
    
    map_result = {'Withdrawn': 0, 'Fail': 1, 'Pass': 2, 'Distinction': 3}
    df_student['final_result_ordinal'] = df_student['final_result'].map(map_result)
    
    return df_student

# ============================================================================
# ORQUESTADOR PIPELINE (EXTRACT - TRANSFORM - LOAD)
# ============================================================================
def ejecutar_etl():
    print("=== INICIANDO PIPELINE ETL OULAD ===")
    engine = obtener_conexion()
    
    # --- CONTROL DE REINTENTOS: LIMPIEZA ADAPTATIVA DE DATOS EXISTENTES ---
    print("\n[Mantenimiento] Vaciando registros previos de forma segura...")
    tablas_en_orden = [
        'student_vle', 
        'student_assessment', 
        'student_registration', 
        'student_info', 
        'assessments', 
        'vle', 
        'courses'
    ]
    
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for tabla in tablas_en_orden:
            conn.execute(text(f"DELETE FROM {tabla};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    print("-> Base de datos vaciada y lista para una carga limpia.")

    # --- PASO 1: Carga de Cursos (courses.csv) ---
    print("\n[1/7] Procesando Cursos...")
    df_courses = pd.read_csv(os.path.join(CSV_DIR, "courses.csv"))
    df_courses.to_sql('courses', con=engine, if_exists='append', index=False)
    print("-> Cursos cargados exitosamente.")

    # --- PASO 2: Carga de Recursos Virtuales (vle.csv) ---
    print("\n[2/7] Procesando Inventario VLE...")
    df_vle = pd.read_csv(os.path.join(CSV_DIR, "vle.csv"))
    df_vle['week_from'] = pd.to_numeric(df_vle['week_from'], errors='coerce').fillna(-1).astype(int)
    df_vle['week_to'] = pd.to_numeric(df_vle['week_to'], errors='coerce').fillna(-1).astype(int)
    df_vle.to_sql('vle', con=engine, if_exists='append', index=False)
    print("-> Componentes VLE cargados exitosamente.")

    # --- PASO 3: Carga de Información de Estudiantes (studentInfo.csv) ---
    print("\n[3/7] Extrayendo y Transformando Demografía de Estudiantes...")
    df_student = pd.read_csv(os.path.join(CSV_DIR, "studentInfo.csv"))
    df_student_transformed = transformar_estudiantes(df_student)
    df_student_transformed.to_sql('student_info', con=engine, if_exists='append', index=False)
    print("-> Datos demográficos con mapeos ordinales insertados.")

    # --- PASO 4: Carga de Registro de Estudiantes (studentRegistration.csv) ---
    print("\n[4/7] Procesando Historial de Registros...")
    df_reg = pd.read_csv(os.path.join(CSV_DIR, "studentRegistration.csv"))
    df_reg['date_registration'] = pd.to_numeric(df_reg['date_registration'], errors='coerce').fillna(0).astype(int)
    df_reg['date_unregistration'] = pd.to_numeric(df_reg['date_unregistration'], errors='coerce').fillna(9999).astype(int)
    df_reg.to_sql('student_registration', con=engine, if_exists='append', index=False)
    print("-> Historial de registro completado.")

    # --- PASO 5: Carga de Estructura de Evaluaciones (assessments.csv) ---
    print("\n[5/7] Procesando Catálogo de Evaluaciones...")
    df_assess = pd.read_csv(os.path.join(CSV_DIR, "assessments.csv"))
    
    df_assess['date'] = pd.to_numeric(df_assess['date'], errors='coerce').fillna(-1).astype(int)
    df_assess = df_assess.rename(columns={'date': 'date_assessment'})
    df_assess['weight'] = pd.to_numeric(df_assess['weight'], errors='coerce').fillna(0.0)
    
    df_assess.to_sql('assessments', con=engine, if_exists='append', index=False)
    print("-> Tabla de evaluaciones mapeada y cargada.")

    # --- PASO 6: Calificaciones Detalladas (studentAssessment.csv) ---
    print("\n[6/7] Cargando Calificaciones de Alumnos (Volumen Alto)...")
    df_student_assess = pd.read_csv(os.path.join(CSV_DIR, "studentAssessment.csv"))
    df_student_assess['score'] = pd.to_numeric(df_student_assess['score'], errors='coerce').fillna(0).astype(int)
    df_student_assess['date_submitted'] = pd.to_numeric(df_student_assess['date_submitted'], errors='coerce').fillna(0).astype(int)
    df_student_assess.to_sql('student_assessment', con=engine, if_exists='append', index=False, chunksize=50000)
    print("-> FullDomain ASSESS poblado correctamente.")

    # --- PASO 7: Interacciones del Entorno Virtual (studentVle.csv) ---
    print("\n[7/7] Cargando Clics en la Plataforma Virtual (Big Data - Procesando en Chunks)...")
    
    # Consulta SQL con cláusula UPSERT nativa para MySQL
    query_upsert = text("""
        INSERT INTO student_vle (code_module, code_presentation, id_student, id_site, date_interaction, sum_click)
        VALUES (:code_module, :code_presentation, :id_student, :id_site, :date_interaction, :sum_click)
        ON DUPLICATE KEY UPDATE sum_click = student_vle.sum_click + VALUES(sum_click);
    """)
    
    chunk_count = 1
    # Usamos chunks de 100,000 para optimizar el envío por red a MySQL
    for chunk in pd.read_csv(os.path.join(CSV_DIR, "studentVle.csv"), chunksize=100000):
        # 1. Adaptación de nombres
        chunk = chunk.rename(columns={'date': 'date_interaction'})
        
        # 2. Tipado estricto y limpieza
        chunk['date_interaction'] = pd.to_numeric(chunk['date_interaction'], errors='coerce').fillna(0).astype(int)
        chunk['sum_click'] = pd.to_numeric(chunk['sum_click'], errors='coerce').fillna(0).astype(int)
        
        # 3. Consolidación interna rápida del bloque
        columnas_clave = ['code_module', 'code_presentation', 'id_student', 'id_site', 'date_interaction']
        chunk = chunk.groupby(columnas_clave, as_index=False)['sum_click'].sum()
        
        # 4. Inserción masiva usando el motor de SQLAlchemy con manejo de duplicados cruzados
        registros = chunk.to_dict(orient='records')
        with engine.begin() as conn:
            conn.execute(query_upsert, registros)
            
        print(f"   -> Subiendo bloque de interacciones virtuales #{chunk_count}...")
        chunk_count += 1
        
    print("-> FullDomain VLE poblado de forma masiva.")
    print("\n=== ¡PIPELINE ETL EJECUTADO CON ÉXITO DE PUNTA A PUNTA! ===")

if __name__ == "__main__":
    ejecutar_etl()