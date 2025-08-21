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

### Структура проєкту
- `main.py` — точка входу; координує логін та парсинг/ставки
- `drivers/browser.py` — ініціалізація WebDriver, утиліти очікувань
- `auth/login.py`, `auth/selectors.py` — логін, MFA
- `scraper/projects.py`, `scraper/selectors.py` — парсинг списку та сторінки проєкту
- `schemas/project.py` — типи даних (Pydantic)
- `ai/client.py`, `ai/prompts.py` — робота з OpenRouter та промпт для генерації повідомлень
- `config/settings.py` — завантаження `.env` і конфігурація

---

### Вимоги
- Встановлений Google Chrome
- Відповідний ChromeDriver (файл `chromedriver.exe` у корені або шлях у `.env`)
- Облікові дані Freelancehunt
- Ключ OpenRouter (для генерації повідомлень)

---

### Установка

Варіант A — через Poetry (рекомендовано):
```bash
pip install poetry
poetry install
```

Варіант B — через venv/pip:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r <буде згенеровано Poetry>  # або: pip install selenium pydantic openai python-dotenv beautifulsoup4 sqlalchemy alembic psycopg-binary
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
DEFAULT_PRICE=1000

# Selenium
# Абсолютний шлях до ChromeDriver (Windows-приклад нижче)
CHROMEDRIVER_PATH=D:\\Desktop\\business\\freelancehunt-automizer\\chromedriver.exe

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_AI_MODEL=meta-llama/llama-3.1-70b-instruct:free

# AI-параметри
AI_TEMPERATURE=0.7
AI_TOP_P=0.9
AI_MAX_TOKENS=512
AI_SYSTEM_CONTENT=You are a helpful assistant
```

Примітка: значення моделі ви можете змінити на будь-яку доступну у вашому акаунті OpenRouter.

---

### Запуск

Poetry:
```bash
poetry run python main.py
```

Або без Poetry (з активованим venv):
```bash
.venv\Scripts\python.exe main.py
```

Під час логіну скрипт попросить **MFA-код** у консолі. Введіть 6-значний код — після успішної перевірки автоматизація продовжиться.

---

### Як це працює (коротко)
1. `main.py` створює `Browser`, `Login` та `ProjectsScraper`.
2. `Login.login()` відкриває сторінку входу, вводить email/пароль, очікує MFA й завершує сесію логіну.
3. `ProjectsScraper.parse_projects()` переходить на сторінку проєктів, збирає список (тема, посилання, кількість ставок).
4. Для кожного посилання `parse_project()`:
   - перевіряє, чи вже подано ставку;
   - зчитує опис, формує промпт (`ai/prompts.py`) і через `ai/client.py` отримує текст повідомлення;
   - відкриває форму, заповнює повідомлення/термін/суму і відправляє.

---

### Поради та усунення несправностей
- **ChromeDriver не сумісний:** оновіть `chromedriver.exe` під вашу версію Chrome та перевірте шлях у `CHROMEDRIVER_PATH`.
- **MFA/вхід не проходить:** перевірте селектори у `auth/selectors.py` (інтерфейс міг змінитись) та значення `.env`.
- **AI не відповідає:** перевірте `OPENROUTER_API_KEY`, ліміти, назву моделі та мережу.
- **Селектори сторінок змінились:** оновіть константи у `scraper/selectors.py`.
- **Cloudflare/anti-bot:** іноді сайти застосовують додаткові перевірки. Запускайте скрипт не надто часто, не використовуйте headless на старті, за потреби додайте очікування.

---

### Безпека
- Зберігайте `.env` поза системами контролю версій.
- Обережно з обліковими даними та API ключами.

---

### Ліцензія
Проєкт поширюється за ліцензією MIT (див. `pyproject.toml`).


