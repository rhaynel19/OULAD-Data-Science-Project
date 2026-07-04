-- ============================================================================
-- MAESTRÍA EN CIENCIA DE DATOS E IA - UASD
-- ASIGNATURA: CIENCIAS DE DATOS I (INF-8237-C2)
-- SCRIPT DDL: MODELO RELACIONAL OULAD CON INTEGRIDAD Y MAPEO ORDINAL (FullDomain)
-- ============================================================================

-- 1. Tabla de Módulos / Cursos
CREATE TABLE courses (
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    module_presentation_length INT,
    PRIMARY KEY (code_module, code_presentation)
);

-- 2. Tabla de Materiales / Recursos del Entorno Virtual (VLE)
CREATE TABLE vle (
    id_site INT PRIMARY KEY,
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    activity_type VARCHAR(50),
    week_from INT,
    week_to INT
);

-- 3. Tabla de Información Demográfica y Académica del Estudiante
CREATE TABLE student_info (
    id_student INT,
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    gender VARCHAR(5),
    gender_ordinal INT, -- Mapeo: 0=F, 1=M
    region VARCHAR(50),
    highest_education VARCHAR(100),
    education_ordinal INT, -- Mapeo: 0=No Formal, 1=Lower Than A Level, 2=A Level, 3=HE Qualification, 4=Post Graduate
    imd_band VARCHAR(20),
    age_band VARCHAR(20),
    age_ordinal INT, -- Mapeo: 0=0-35, 1=35-55, 2=55<=
    num_of_prev_attempts INT,
    studied_credits INT,
    disability VARCHAR(5),
    disability_ordinal INT, -- Mapeo: 0=N, 1=Y
    final_result VARCHAR(20),
    final_result_ordinal INT, -- Mapeo: 0=Withdrawn, 1=Fail, 2=Pass, 3=Distinction
    PRIMARY KEY (id_student, code_module, code_presentation),
    FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation)
);

-- 4. Tabla de Registro de Estudiantes
CREATE TABLE student_registration (
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    id_student INT,
    date_registration INT,
    date_unregistration INT,
    PRIMARY KEY (code_module, code_presentation, id_student),
    FOREIGN KEY (id_student, code_module, code_presentation) REFERENCES student_info(id_student, code_module, code_presentation)
);

-- 5. Tabla de Estructura de Evaluaciones (ASSESS)
CREATE TABLE assessments (
    id_assessment INT PRIMARY KEY,
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    assessment_type VARCHAR(10),
    date_assessment INT,
    weight DECIMAL(5,2),
    FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation)
);

-- 6. Tabla de Calificaciones por Estudiante (FullDomain - ASSESS DETAILED)
CREATE TABLE student_assessment (
    id_assessment INT,
    id_student INT,
    date_submitted INT,
    is_banked INT,
    score INT,
    PRIMARY KEY (id_assessment, id_student),
    FOREIGN KEY (id_assessment) REFERENCES assessments(id_assessment)
);

-- 7. Tabla de Interacciones de Clics (FullDomain - VLE DETAILED)
CREATE TABLE student_vle (
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    id_student INT,
    id_site INT,
    date_interaction INT,
    sum_click INT,
    PRIMARY KEY (code_module, code_presentation, id_student, id_site, date_interaction),
    FOREIGN KEY (id_site) REFERENCES vle(id_site)
);