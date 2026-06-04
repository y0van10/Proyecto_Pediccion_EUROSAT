#!/bin/bash
set -e

echo "🚀 Iniciando despliegue de EuroSAT AI..."

# Verificar si el modelo existe
if [ ! -f "backend/model/satellite_classifier.keras" ]; then
    echo "⚠️  ADVERTENCIA: No se encontró el modelo en backend/model/satellite_classifier.keras"
    echo "   El backend se ejecutará en modo MOCK (simulación)."
fi

# Construir e iniciar contenedores
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "✅ Despliegue completado."
echo "🌍 Accede a: http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'localhost')"
echo "📊 API Docs: http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'localhost')/docs"
echo "🔍 Health:   http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'localhost')/api/v1/health"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs:     docker compose logs -f"
echo "   Detener:      docker compose down"
echo "   Reiniciar:    docker compose restart"
