# Script de inicio rápido - Zaragoza Histórica (Python Stack)
# PowerShell script para iniciar backend Python y frontend React

Write-Host "🏛️ Iniciando Zaragoza Histórica - Stack Python..." -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está corriendo
Write-Host "📦 Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Docker no está corriendo." -ForegroundColor Red
    Write-Host "   Por favor, inicia Docker Desktop e intenta de nuevo." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Docker está corriendo" -ForegroundColor Green
Write-Host ""
Write-Host "🐘 Iniciando PostgreSQL + Backend Python..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Backend y base de datos iniciados" -ForegroundColor Green
Start-Sleep -Seconds 5

# Verificar que el backend esté funcionando
Write-Host "🔍 Verificando API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API funcionando correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  API aún iniciando (esto es normal)..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎨 Iniciando Frontend (puerto 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\pvial\Desktop\TFG DAM v2\frontend' ; npm run dev"

Write-Host ""
Write-Host "✨ ¡Listo! Abriendo navegador en 5 segundos..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   • Frontend:    http://localhost:5173" -ForegroundColor Yellow
Write-Host "   • Backend API: http://localhost:3000/api" -ForegroundColor Gray
Write-Host "   • API Docs:    http://localhost:3000/docs" -ForegroundColor Green
Write-Host "   • Health:      http://localhost:3000/api/health" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Stack: Python + FastAPI | React + TypeScript | PostgreSQL + PostGIS" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host "✅ Aplicación iniciada." -ForegroundColor Green
Write-Host "   Para detener: ejecuta .\stop.ps1" -ForegroundColor Gray
Write-Host ""

# Mantener el script abierto
Read-Host "Presiona Enter para cerrar"
