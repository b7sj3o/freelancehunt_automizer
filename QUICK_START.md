# 🚀 Швидкий старт - Freelancehunt Automizer GUI

## 📱 Запуск GUI додатку

### Windows:
```batch
# Простий запуск
run_gui.bat

# Або через PowerShell
.\run_gui.ps1

# Або через Poetry
poetry run python gui_app.py
```

## 📦 Створення .exe файлу

### Windows:
```batch
# Простий запуск збірки
build.bat

# Або через PowerShell  
.\build.ps1

# Або через Poetry
poetry run python build_exe.py
```

## 🧪 Тестування

```bash
# Перевірка готовності
poetry run python test_gui.py
```

## 📂 Структура файлів

```
📁 freelancehunt-automizer/
├── 🖥️ gui_app.py              # Точка входу GUI
├── 📱 gui/main_window.py       # Головний GUI модуль
├── 🔨 build_exe.py            # Збірка .exe
├── 🧪 test_gui.py             # Тестування
├── 📝 GUI_INSTRUCTIONS.md     # Детальна інструкція
├── ⚡ run_gui.bat             # Швидкий запуск (Batch)
├── ⚡ run_gui.ps1             # Швидкий запуск (PowerShell)
├── 🔨 build.bat              # Швидка збірка (Batch)
├── 🔨 build.ps1              # Швидка збірка (PowerShell)
└── 📦 dist/                   # Готовий .exe файл (після збірки)
```

## 🎯 Що далі?

1. **Запустіть GUI**: `run_gui.bat`
2. **Налаштуйте параметри** у вкладці "Налаштування"
3. **Запустіть автоматизацію** у вкладці "Автоматизація"
4. **Переглядайте результати** у вкладці "Проекти"
5. **Створіть .exe** для зручності: `build.bat`

## 🆘 Проблеми?

- Перевірте `GUI_INSTRUCTIONS.md` для детальної інформації
- Запустіть `test_gui.py` для діагностики
- Переглядайте логи в папці `logs/`
