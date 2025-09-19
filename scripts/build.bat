@echo off
echo 🚀 Freelancehunt Automizer - Build Script
echo ==========================================

echo.
echo 📦 Встановлення залежностей...
poetry install

echo.
echo 🔨 Збірка .exe файлу...
poetry run python build_exe.py

echo.
echo ✅ Готово! Перевірте папку dist/
pause
