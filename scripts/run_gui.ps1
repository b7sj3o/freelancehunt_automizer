#!/usr/bin/env pwsh
# Запуск Freelancehunt Automizer GUI (PowerShell)

Write-Host "🖥️ Запуск Freelancehunt Automizer GUI" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Запуск GUI додатку..." -ForegroundColor Yellow
poetry run python gui_app.py

Write-Host ""
Write-Host "Програма завершена." -ForegroundColor Gray
