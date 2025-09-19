#!/usr/bin/env python3
"""
Скрипт для збірки .exe файлу Freelancehunt Automizer GUI
"""

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

def build_exe():
    # Параметри для PyInstaller
    args = [
        'gui_app.py',  # Головний файл
        '--onefile',   # Один exe файл
        '--windowed',  # Без консольного вікна
        '--name=FreelancehuntAutomizer',  # Назва exe файлу
        '--icon=assets/icon.ico' if os.path.exists('assets/icon.ico') else '',  # Іконка (якщо є)
        '--add-data=gui;gui',  # Додаємо gui папку
        '--add-data=chromedriver.exe;.',  # Додаємо chromedriver
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=selenium',
        '--hidden-import=sqlalchemy',
        '--hidden-import=psycopg2',
        '--hidden-import=openai',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=pydantic',
        '--hidden-import=alembic',
        '--collect-all=selenium',
        '--collect-all=sqlalchemy',
        '--distpath=dist',  # Папка для результату
        '--workpath=build',  # Папка для тимчасових файлів
        '--clean',  # Очистити попередні збірки
    ]
    
    # Видаляємо пусті аргументи
    args = [arg for arg in args if arg]
    
    print("🔨 Початок збірки .exe файлу...")
    print(f"Аргументи PyInstaller: {args}")
    
    try:
        # Запускаємо PyInstaller
        PyInstaller.__main__.run(args)
        
        print("✅ Збірка завершена успішно!")
        print(f"📁 Результат знаходиться в папці: {os.path.abspath('dist')}")
        
        # Перевіряємо чи створився exe файл
        exe_path = Path("dist/FreelancehuntAutomizer.exe")
        if exe_path.exists():
            print(f"🎉 Exe файл створено: {exe_path.absolute()}")
            print(f"📏 Розмір файлу: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("❌ Exe файл не знайдено в папці dist")
            
    except Exception as e:
        print(f"❌ Помилка під час збірки: {e}")
        return False
        
    return True

def create_installer_files():
    """Створює додаткові файли для інсталятора"""
    
    # Створюємо README для exe
    readme_content = """
# Freelancehunt Automizer

## Інструкція по використанню:

1. Переконайтеся що у вас встановлений Google Chrome
2. Створіть файл .env в папці з програмою з наступним вмістом:

```
# Freelancehunt
FREELANCEHUNT_LOGIN_PAGE=https://freelancehunt.com/login
FREELANCEHUNT_PROJECTS_PAGE=https://freelancehunt.com/projects
FREELANCEHUNT_EMAIL=your_email@example.com
FREELANCEHUNT_PASSWORD=your_password

# AI
OPENROUTER_API_KEY=sk-or-your-key
OPENROUTER_AI_MODEL=openai/gpt-4o-mini

# Налаштування
DEFAULT_DAYS=3
DEFAULT_PRICE=1000
```

3. Запустіть FreelancehuntAutomizer.exe
4. Налаштуйте параметри в GUI
5. Запустіть автоматизацію

## Підтримка:
Якщо виникли проблеми, перевірте логи в папці logs/
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    print("📝 Створено README.txt")

def main():
    print("🚀 Freelancehunt Automizer - Збірка EXE файлу")
    print("=" * 50)
    
    # Перевіряємо чи встановлений PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller версія: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller не встановлений!")
        print("Встановіть його командою: pip install pyinstaller")
        return False
    
    # Перевіряємо наявність головного файлу
    if not os.path.exists("gui_app.py"):
        print("❌ Файл gui_app.py не знайдено!")
        return False
    
    # Створюємо папки якщо не існують
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # Збираємо exe
    if build_exe():
        create_installer_files()
        print("\n🎉 Збірка завершена успішно!")
        print("📦 Файли для розповсюдження знаходяться в папці dist/")
        return True
    else:
        print("\n❌ Збірка не вдалась!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
