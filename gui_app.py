#!/usr/bin/env python3
"""
Головний файл для запуску GUI версії Freelancehunt Automizer
"""

import sys
import os
from pathlib import Path

# Визначаємо папку з програмою
if getattr(sys, 'frozen', False):
    # Якщо запущено як .exe файл
    current_dir = Path(sys.executable).parent
else:
    # Якщо запущено як Python скрипт
    current_dir = Path(__file__).parent

# Встановлюємо робочу директорію
os.chdir(current_dir)

# Додаємо кореневу папку до sys.path
sys.path.insert(0, str(current_dir))

# Створюємо папку gui якщо не існує
gui_dir = current_dir / "gui"
gui_dir.mkdir(exist_ok=True)

# Додаємо gui папку до sys.path
sys.path.insert(0, str(gui_dir))

def main():
    try:
        from gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Помилка імпорту GUI модулів: {e}")
        print("Переконайтеся, що всі залежності встановлені.")
        sys.exit(1)
    except Exception as e:
        print(f"Помилка запуску GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
