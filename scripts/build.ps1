#!/usr/bin/env pwsh
# Freelancehunt Automizer Build Script (PowerShell)

Write-Host "🚀 Freelancehunt Automizer - Build Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host ""
Write-Host "📦 Встановлення залежностей..." -ForegroundColor Yellow
poetry install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Помилка встановлення залежностей!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔨 Збірка .exe файлу..." -ForegroundColor Yellow
poetry run python build_exe.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Помилка збірки!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Готово! Перевірте папку dist/" -ForegroundColor Green

# Відкриваємо папку з результатом
if (Test-Path "dist") {
    Write-Host "📁 Відкриваємо папку dist..." -ForegroundColor Cyan
    Invoke-Item "dist"
}

Write-Host ""
Write-Host "Натисніть будь-яку клавішу для завершення..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
