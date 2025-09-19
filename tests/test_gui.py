#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки GUI додатку
"""

import sys
import os
from pathlib import Path

# Додаємо кореневу папку до sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Тестує чи всі необхідні модулі можна імпортувати"""
    print("🧪 Тестування імпортів...")
    
    try:
        import tkinter as tk
        print("✅ tkinter - OK")
    except ImportError as e:
        print(f"❌ tkinter - FAIL: {e}")
        return False
    
    try:
        from tkinter import ttk
        print("✅ tkinter.ttk - OK")
    except ImportError as e:
        print(f"❌ tkinter.ttk - FAIL: {e}")
        return False
    
    try:
        import threading
        print("✅ threading - OK")
    except ImportError as e:
        print(f"❌ threading - FAIL: {e}")
        return False
        
    try:
        from gui.main_window import FreelancehuntGUI
        print("✅ GUI модулі - OK")
    except ImportError as e:
        print(f"❌ GUI модулі - FAIL: {e}")
        return False
        
    try:
        from db.requests import get_all_projects
        print("✅ Database модулі - OK")
    except ImportError as e:
        print(f"❌ Database модулі - FAIL: {e}")
        return False
        
    return True

def test_gui_creation():
    """Тестує створення GUI вікна"""
    print("\n🖥️ Тестування створення GUI...")
    
    try:
        import tkinter as tk
        from gui.main_window import FreelancehuntGUI
        
        # Створюємо тестове вікно
        root = tk.Tk()
        root.withdraw()  # Ховаємо вікно
        
        app = FreelancehuntGUI(root)
        print("✅ GUI створено успішно")
        
        # Закриваємо вікно
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення GUI: {e}")
        return False

def test_database_connection():
    """Тестує підключення до бази даних"""
    print("\n💾 Тестування підключення до БД...")
    
    try:
        from db.requests import get_all_projects
        projects = get_all_projects()
        print(f"✅ База даних доступна, проектів: {len(projects)}")
        return True
    except Exception as e:
        print(f"❌ Помилка підключення до БД: {e}")
        return False

def test_file_structure():
    """Перевіряє наявність необхідних файлів"""
    print("\n📁 Перевірка структури файлів...")
    
    required_files = [
        "gui_app.py",
        "gui/main_window.py", 
        "build_exe.py",
        "run_gui.bat",
        "run_gui.ps1",
        "build.bat",
        "build.ps1"
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - відсутній")
            all_ok = False
            
    return all_ok

def main():
    print("🚀 Freelancehunt Automizer GUI - Тестування")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Тест 1: Імпорти
    if test_imports():
        tests_passed += 1
        
    # Тест 2: Структура файлів
    if test_file_structure():
        tests_passed += 1
        
    # Тест 3: База даних
    if test_database_connection():
        tests_passed += 1
        
    # Тест 4: GUI створення
    if test_gui_creation():
        tests_passed += 1
    
    print(f"\n📊 Результати тестування:")
    print(f"Пройдено тестів: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Всі тести пройдено успішно!")
        print("✅ GUI додаток готовий до використання")
        return True
    else:
        print("⚠️ Деякі тести не пройдено")
        print("❌ Потрібно виправити помилки перед використанням")
        return False

if __name__ == "__main__":
    success = main()
    
    print(f"\nДля запуску GUI використовуйте:")
    print("poetry run python gui_app.py")
    print("або")
    print("run_gui.bat")
    
    sys.exit(0 if success else 1)
