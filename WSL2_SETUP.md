# Guía de Configuración y Entrenamiento en WSL2 (GPU CUDA)

Sigue estos pasos para entrenar los modelos de clasificación de imágenes jerárquicos utilizando tu GPU NVIDIA bajo Windows Subsystem for Linux (WSL2).

---

## Requisitos Previos en Windows
1. Asegúrate de tener instalado el último driver oficial de NVIDIA en Windows. **WSL2 comparte automáticamente la GPU de Windows**, por lo que no debes instalar controladores de GPU dentro de Linux.
2. Abre la terminal (PowerShell o cmd) y confirma que tu versión de WSL2 está actualizada:
   ```bash
   wsl --update
   wsl --status
   ```

---

## 1. Configuración del Entorno dentro de WSL2 (Ubuntu)

Abre tu terminal de WSL2 (ej. Ubuntu) y ejecuta los siguientes comandos:

### Actualizar paquetes del sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

### Crear y Activar Entorno Virtual (Venv)
Es recomendable aislar las dependencias:
```bash
# Navegar al directorio de entrenamiento
cd "/mnt/c/Users/INTEL/Documents/UNA-Puno/9no SEMESTRE/APRENDIZAJE_PROFUNDO/practicafinal/proyecto_prediccion/training"

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate
```

### Instalar dependencias requeridas
Instala TensorFlow 2.16+ y las bibliotecas científicas necesarias:
```bash
pip install --upgrade pip
pip install tensorflow[and-cuda]==2.16.1 uvicorn fastapi python-multipart pillow numpy scikit-learn matplotlib
```
> **Nota**: `tensorflow[and-cuda]` descarga e instala automáticamente las bibliotecas dinámicas de CUDA y cuDNN en el entorno virtual de Python, eliminando la necesidad de configurar CUDA manualmente en Ubuntu.

---

## 2. Iniciar el Entrenamiento (En Orden)

Una vez activado el entorno, puedes iniciar la descarga de datasets y el entrenamiento con GPU en la terminal:

### Paso A: Entrenar Clasificador Satelital (EuroSAT)
Este script descarga el dataset EuroSAT (~90MB), aplica aumento de datos y entrena usando EfficientNetV2-B0:
```bash
python train_satellite.py
```
*Se guardará el mejor modelo en `../backend/model/satellite_classifier.keras`.*

### Paso B: Entrenar Clasificador Terrestre (Paisajes Naturales)
Este script descarga un subconjunto de paisajes terrestres de Intel (~25MB) y entrena un modelo especializado:
```bash
python train_terrestrial.py
```
*Se guardará el mejor modelo en `../backend/model/terrestrial_classifier.keras`.*

### Paso C: Entrenar Clasificador de Dominio (Satelital vs Terrestre)
Este script extrae de forma balanceada imágenes de satélite y terrestre y entrena un clasificador binario ultraligero:
```bash
python train_domain.py
```
*Se guardará el modelo de enrutamiento en `../backend/model/domain_classifier.keras`.*

### Paso D: Generar Métricas y Matrices de Confusión
Calcula el F1-Score, Precisión y genera las gráficas de validación para la sustentación universitaria:
```bash
python generate_plots.py
```
*Las gráficas se guardarán en el nuevo directorio `results/`.*

---

## 3. Integración con el Backend
Al terminar el entrenamiento, los tres modelos (`domain_classifier.keras`, `satellite_classifier.keras`, y `terrestrial_classifier.keras`) quedarán guardados en la carpeta `backend/model/` listos para ser consumidos por la API FastAPI.
