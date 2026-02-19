# Script para detener todos los servicios - Zaragoza Histórica

Write-Host "🛑 Deteniendo Zaragoza Histórica..." -ForegroundColor Yellow
Write-Host ""

# Detener Docker Compose
Write-Host "🐘 Deteniendo PostgreSQL..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✅ Servicios detenidos" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Recuerda cerrar manualmente las ventanas de PowerShell del backend y frontend" -ForegroundColor Yellow

Read-Host "Presiona Enter para cerrar"
