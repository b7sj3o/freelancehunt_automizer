### Freelancehunt Automizer

Автоматизатор для перегляду проєктів на Freelancehunt та напівавтоматичної подачі заявок за допомогою Selenium і AI (через OpenRouter). Скрипт логіниться, парсить список проєктів, визначає чи вже була подана ставка, генерує повідомлення та заповнює форму.

---

### Основні можливості
- **Логін з MFA**: скрипт чекає на введення коду в консоль.
- **Парсинг списку проєктів** та переходи у картку проєкту.
- **Перевірка** чи вже зроблено ставку.
- **Генерація повідомлення** для заявки на основі опису (AI через OpenRouter).
- **Заповнення форми**: повідомлення, терміни, ціна; відправка заявки.

---

### Стек
- Python 3.12+
- Selenium 4
- OpenRouter (сумісний з OpenAI SDK) для LLM
- Poetry для керування залежностями

---

### Вимоги
- Встановлений Google Chrome
- Відповідний ChromeDriver (файл `chromedriver.exe` у корені або шлях у `.env`)
- Облікові дані Freelancehunt
- Ключ OpenRouter (для генерації повідомлень)

---

### Установка

1. Встановлення pipx - скористайтесь <a href="https://pipx.pypa.io/stable/installation/">цією документацією</a>

2. Встановлення Poetry:
```bash
pipx install poetry
```

3. Встановлення залежностей:
```bash
poetry install
```

---

### Налаштування оточення
Створіть файл `.env` у корені проєкту і заповніть змінні:
```env
# Freelancehunt
FREELANCEHUNT_LOGIN_PAGE=https://freelancehunt.com/login
FREELANCEHUNT_PROJECTS_PAGE=https://freelancehunt.com/projects
FREELANCEHUNT_EMAIL=you@example.com
FREELANCEHUNT_PASSWORD=your_password

# Значення за замовчуванням для заявки
DEFAULT_DAYS=3
DEFAULT_PRICE_UAH=1000

# Selenium
# Абсолютний шлях до ChromeDriver (Windows-приклад нижче)
CHROMEDRIVER_PATH=D:\\Projects\\freelancehunt-automizer\\chromedriver.exe

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_AI_MODEL=openai/gpt-oss-120b 

# AI-параметри (мої налаштування, які чудово працюють)
AI_TEMPERATURE=0.5
AI_TOP_P=0.95
AI_MAX_TOKENS=1000
AI_SYSTEM_CONTENT="Language answer: ..."
```

Примітка: значення моделі ви можете змінити на будь-яку доступну у вашому акаунті OpenRouter.

---

### Запуск

#### Консольна версія:
```bash
poetry run python main.py
```

#### GUI версія:
```bash
# Запуск GUI додатку
poetry run python gui_app.py

# Або використовуйте готові скрипти:
# Windows (Batch)
run_gui.bat

# Windows (PowerShell)
.\run_gui.ps1
```

#### Збірка .exe файлу:
```bash
# Збірка executable файлу
poetry run python build_exe.py

# Або використовуйте готові скрипти:
# Windows (Batch)
build.bat

# Windows (PowerShell)
.\build.ps1
```

Після збірки .exe файл буде знаходитися в папці `dist/`.

Під час логіну скрипт попросить **MFA-код** у консолі або GUI. Введіть 6-значний код — після успішної перевірки автоматизація продовжиться.

---

### GUI Функціонал

Desktop додаток включає:

- **Налаштування**: Зручне налаштування всіх параметрів через GUI
- **Автоматизація**: Запуск парсингу та розміщення ставок з прогрес-баром
- **Перегляд проектів**: Таблиця всіх проектів з фільтрацією та статистикою
- **Логи**: Перегляд та очищення лог файлів
- **Статистика**: Кількість активних проектів, розміщених ставок тощо

---


