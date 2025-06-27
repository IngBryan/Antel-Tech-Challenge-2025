# Automatización de Reportes SLA - Antel Tech Challenge 2025

Este proyecto fue desarrollado para el **IA TECH CHALLENGE 2025**, en colaboración con la empresa **Accesa**, **Antel**, **ANNI** y **Google**.  
El objetivo fue automatizar la generación de reportes SLA a partir de archivos .csv, .xlsx y .xls, utilizando servicios de Google Cloud como **Vertex AI** y **Cloud Storage**.

---

## Tecnologías utilizadas

- **Python 3**
- **Flask** 
- **Vertex AI**
- **Google Cloud Storage (Buckets)**
- **Pandas**
- **ReportLab** 
- **OpenPyXL** y **xlrd** (manejo de Excel)
- **PyJWT** (autenticación con JSON Web Tokens)
- **dotenv** (configuración por variables de entorno)
- **Gunicorn** (servidor WSGI utilizado en el entorno de "producción")
---

##  Instalación y ejecución

### 1. Clonar el repositorio

  git clone https://github.com/IngBryan/Antel-Tech-Challenge-2025.git
  
### 2. Crear un entorno virtual (opcional)
  python -m venv venv
  source venv/bin/activate  # En Windows: venv\Scripts\activate

### 3. Instalar dependencias
  pip install -r requirements.txt

### 4. Configuración del entorno
En la raíz del proyecto y dentro de la carpeta src deben estar presentes el siguiente archivo:

**ai.json**
Clave de una cuenta de servicio de Google Cloud que tenga permisos para:

  -Leer y escribir en el bucket
  -Utilizar Vertex AI

Se puede generar desde Google Cloud Console > IAM & Admin > Service Accounts.

### 5. .env 
Este archivo define las variables necesarias para SLA y acceso:
  ##### VARIABLES SLA
  NIVEL_DEL_SERVICIO=80/20
  
  ABANDONO=10%
  
  TRSAC=40  # SEGUNDOS
  
  CONGESTION=5%

  ##### CREDENCIALES DE AUTENTICACIÓN
  USUARIO=accesa
  
  CONTRASENA=equipo2
  
  ##### CONFIGURACIÓN GOOGLE CLOUD
  CLAVE=ai.json
  
  NOMBRE_BUCKET=docs_equipo2
  
  RUTA_ARCHIVO=csvs/procesar/
  
  RUTA_PROCESADOS=csvs/procesados/
