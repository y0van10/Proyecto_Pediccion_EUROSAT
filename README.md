# EuroSAT Satellite Classification Project

Este proyecto es una plataforma profesional de clasificación de imágenes satelitales basada en el dataset EuroSAT, utilizando Deep Learning (EfficientNetB0), Next.js 15 y FastAPI.

## Estructura del Proyecto
- `frontend/`: Aplicación Next.js con Tailwind CSS y Framer Motion.
- `backend/`: API FastAPI con TensorFlow para inferencia de modelos.
- `nginx/`: Configuración de proxy inverso para producción.

## Requisitos Previos
- Docker y Docker Compose
- Ubuntu 24.04+ (Recomendado para producción)
- Archivo de modelo: `backend/model/modelo_final_eurosat.keras`

## Despliegue con Docker (Recomendado)

1. Clonar el repositorio.
2. Colocar su archivo `.keras` en `backend/model/`.
3. Ejecutar el comando:
   ```bash
   docker compose up -d --build
   ```
4. Acceder a `http://localhost`.

## Comandos de Instalación en Ubuntu Server

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-v2 -y

# Clonar proyecto (ejemplo)
# git clone <repo_url>
cd proyecto_prediccion

# Iniciar producción
sudo docker compose up -d
```

## Scripts de Mantenimiento
- Ver logs: `docker compose logs -f`
- Detener: `docker compose down`
- Reiniciar: `docker compose restart`

## Autores
- Proyecto Universitario Deep Learning - UNA Puno
