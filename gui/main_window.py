import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import os
from datetime import datetime
import sys
import json
from pathlib import Path

# Додаємо кореневу папку до sys.path для імпорту модулів
sys.path.append(str(Path(__file__).parent.parent))

from main import Main
from db.requests import get_all_projects, get_active_projects
from core.config import settings
from core.logger_config import setup_logger
from auth.gui_login import GUILogin
from drivers.browser import Browser

logger = setup_logger(name="gui", log_file="gui.log")


class MFADialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("2FA Код")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центруємо діалог
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Створюємо інтерфейс
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Введіть 6-значний 2FA код:", 
                 font=('Arial', 10)).pack(pady=(0, 10))
        
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(main_frame, textvariable=self.code_var, 
                                   font=('Arial', 14), justify='center', width=10)
        self.code_entry.pack(pady=(0, 10))
        self.code_entry.focus()
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Скасувати", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Прив'язуємо Enter до OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        
    def ok_clicked(self):
        code = self.code_var.get().strip()
        if len(code) == 6 and code.isdigit():
            self.result = code
            self.dialog.destroy()
        else:
            messagebox.showerror("Помилка", "Код повинен містити рівно 6 цифр")
            self.code_entry.focus()
            
    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        self.dialog.wait_window()
        return self.result


class FreelancehuntGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Freelancehunt Automizer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Стилі
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Змінні стану
        self.is_running = False
        self.automation_thread = None
        self.mfa_code = None
        self.mfa_requested = False
        
        # Створюємо інтерфейс
        self.create_widgets()
        
        # Завантажуємо налаштування
        self.load_settings()
        
        # Оновлюємо список проектів
        self.refresh_projects()
        
    def create_widgets(self):
        # Головний notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка налаштувань
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Налаштування")
        self.create_settings_tab()
        
        # Вкладка автоматизації
        self.automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.automation_frame, text="Автоматизація")
        self.create_automation_tab()
        
        # Вкладка проектів
        self.projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_frame, text="Проекти")
        self.create_projects_tab()
        
        # Вкладка логів
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Логи")
        self.create_logs_tab()
        
    def create_settings_tab(self):
        # Фрейм для налаштувань
        main_frame = ttk.Frame(self.settings_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Freelancehunt налаштування
        fh_frame = ttk.LabelFrame(main_frame, text="Freelancehunt", padding=15)
        fh_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fh_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(fh_frame, textvariable=self.email_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(fh_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(fh_frame, textvariable=self.password_var, show="*", width=40).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(fh_frame, text="URL проектів:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.projects_url_var = tk.StringVar()
        ttk.Entry(fh_frame, textvariable=self.projects_url_var, width=40).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # AI налаштування
        ai_frame = ttk.LabelFrame(main_frame, text="AI (OpenRouter)", padding=15)
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ai_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(ai_frame, textvariable=self.api_key_var, show="*", width=40).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(ai_frame, text="Модель:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        ttk.Entry(ai_frame, textvariable=self.model_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Налаштування заявок
        bid_frame = ttk.LabelFrame(main_frame, text="Параметри заявок", padding=15)
        bid_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(bid_frame, text="Дні за замовчуванням:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.days_var = tk.StringVar()
        ttk.Entry(bid_frame, textvariable=self.days_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(bid_frame, text="Ціна за замовчуванням (UAH):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(bid_frame, textvariable=self.price_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Зберегти налаштування", 
                  command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Завантажити з .env", 
                  command=self.load_from_env).pack(side=tk.LEFT)
        
    def create_automation_tab(self):
        main_frame = ttk.Frame(self.automation_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Контрольна панель
        control_frame = ttk.LabelFrame(main_frame, text="Керування", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Налаштування парсингу
        ttk.Label(control_frame, text="Сторінки для парсингу:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pages_var = tk.StringVar(value="1-5")
        ttk.Entry(control_frame, textvariable=self.pages_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(control_frame, text="(приклад: 5 або 1-10)").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Кнопки керування
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=20, sticky=tk.W)
        
        self.start_button = ttk.Button(button_frame, text="Запустити автоматизацію", 
                                      command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Зупинити", 
                                     command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Тільки парсинг", 
                  command=self.parse_only).pack(side=tk.LEFT)
        
        # Статус
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Готовий до запуску")
        ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 12)).pack()
        
        # Прогрес бар
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Лог консоль
        log_frame = ttk.LabelFrame(main_frame, text="Лог виконання", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Текстове поле з прокруткою
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка очистки логу
        ttk.Button(log_frame, text="Очистити лог", 
                  command=self.clear_log).pack(pady=(10, 0))
        
    def create_projects_tab(self):
        main_frame = ttk.Frame(self.projects_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Контрольна панель
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Оновити", 
                  command=self.refresh_projects).pack(side=tk.LEFT, padx=(0, 10))
        
        # Фільтри
        ttk.Label(control_frame, text="Фільтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(control_frame, textvariable=self.filter_var, 
                                   values=["Всі", "Активні", "Зі ставками", "Пропущені"], width=15)
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_projects)
        filter_combo.set("Всі")
        
        # Статистика
        self.stats_var = tk.StringVar()
        ttk.Label(control_frame, textvariable=self.stats_var).pack(side=tk.RIGHT)
        
        # Таблиця проектів
        columns = ("ID", "Назва", "Ціна", "Статус", "Дата")
        self.projects_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Налаштування колонок
        self.projects_tree.heading("ID", text="ID")
        self.projects_tree.heading("Назва", text="Назва проекту")
        self.projects_tree.heading("Ціна", text="Ціна (UAH)")
        self.projects_tree.heading("Статус", text="Статус")
        self.projects_tree.heading("Дата", text="Дата")
        
        self.projects_tree.column("ID", width=50, minwidth=50)
        self.projects_tree.column("Назва", width=400, minwidth=200)
        self.projects_tree.column("Ціна", width=100, minwidth=80)
        self.projects_tree.column("Статус", width=150, minwidth=100)
        self.projects_tree.column("Дата", width=120, minwidth=100)
        
        # Прокрутка для таблиці
        tree_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстне меню
        self.create_context_menu()
        
    def create_logs_tab(self):
        main_frame = ttk.Frame(self.logs_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Вибір лог файлу
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Лог файл:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_file_var = tk.StringVar()
        log_files = ["main.log", "gui.log", "projects_scraper.log", "browser.log", "requests.log"]
        log_combo = ttk.Combobox(control_frame, textvariable=self.log_file_var, 
                                values=log_files, width=20)
        log_combo.pack(side=tk.LEFT, padx=(0, 10))
        log_combo.bind('<<ComboboxSelected>>', self.load_log_file)
        log_combo.set("gui.log")
        
        ttk.Button(control_frame, text="Оновити", 
                  command=self.load_log_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Очистити", 
                  command=self.clear_log_file).pack(side=tk.LEFT)
        
        # Текстове поле для логів
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_display = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_display.yview)
        self.log_display.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Завантажуємо початковий лог
        self.load_log_file()
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Відкрити посилання", command=self.open_project_link)
        self.context_menu.add_command(label="Копіювати посилання", command=self.copy_project_link)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Видалити проект", command=self.delete_project)
        
        self.projects_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        item = self.projects_tree.identify_row(event.y)
        if item:
            self.projects_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_project_link(self):
        selected = self.projects_tree.selection()
        if selected:
            # Тут можна додати логіку відкриття посилання
            pass
            
    def copy_project_link(self):
        selected = self.projects_tree.selection()
        if selected:
            # Тут можна додати логіку копіювання посилання
            pass
            
    def delete_project(self):
        selected = self.projects_tree.selection()
        if selected:
            # Тут можна додати логіку видалення проекту
            pass
        
    def save_settings(self):
        settings_data = {
            "email": self.email_var.get(),
            "password": self.password_var.get(),
            "projects_url": self.projects_url_var.get(),
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "default_days": self.days_var.get(),
            "default_price": self.price_var.get()
        }
        
        try:
            with open("gui_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успіх", "Налаштування збережено!")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
            
    def load_settings(self):
        try:
            if os.path.exists("gui_settings.json"):
                with open("gui_settings.json", "r", encoding="utf-8") as f:
                    settings_data = json.load(f)
                    
                self.email_var.set(settings_data.get("email", ""))
                self.password_var.set(settings_data.get("password", ""))
                self.projects_url_var.set(settings_data.get("projects_url", ""))
                self.api_key_var.set(settings_data.get("api_key", ""))
                self.model_var.set(settings_data.get("model", "openai/gpt-4o-mini"))
                self.days_var.set(settings_data.get("default_days", "3"))
                self.price_var.set(settings_data.get("default_price", "1000"))
        except Exception as e:
            logger.error(f"Помилка завантаження налаштувань: {e}")
            
    def load_from_env(self):
        try:
            self.email_var.set(getattr(settings, 'FREELANCEHUNT_EMAIL', ''))
            self.password_var.set(getattr(settings, 'FREELANCEHUNT_PASSWORD', ''))
            self.projects_url_var.set(getattr(settings, 'FREELANCEHUNT_PROJECTS_PAGE', ''))
            self.api_key_var.set(getattr(settings, 'OPENROUTER_API_KEY', ''))
            self.model_var.set(getattr(settings, 'OPENROUTER_AI_MODEL', 'openai/gpt-4o-mini'))
            self.days_var.set(str(getattr(settings, 'DEFAULT_DAYS', 3)))
            self.price_var.set(str(getattr(settings, 'DEFAULT_PRICE', 1000)))
            messagebox.showinfo("Успіх", "Налаштування завантажено з .env файлу!")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити з .env: {e}")
            
    def start_automation(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        self.status_var.set("Запуск автоматизації...")
        self.log_message("🚀 Запуск автоматизації...")
        
        # Запускаємо в окремому потоці
        self.automation_thread = threading.Thread(target=self.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def run_automation(self):
        try:
            # Тут викликаємо основну логіку
            main_app = Main()
            
            # Створюємо GUI версію логіну з callback для MFA
            gui_login = GUILogin(main_app.browser, mfa_callback=self._get_mfa_code_from_thread)
            
            # Спочатку логінимось
            self.root.after(0, lambda: self.status_var.set("Авторизація..."))
            self.root.after(0, lambda: self.log_message("🔐 Початок авторизації..."))
            
            # Викликаємо функцію логіну
            login_success = gui_login.login()
            if not login_success:
                self.root.after(0, lambda: self.log_message("❌ Помилка авторизації"))
                self.root.after(0, lambda: self.status_var.set("Помилка авторизації"))
                return
                
            self.root.after(0, lambda: self.log_message("✅ Авторизація успішна"))
            
            # Переходимо на сторінку проектів
            projects_url = self.projects_url_var.get().strip()
            if projects_url:
                self.root.after(0, lambda: self.log_message(f"🌐 Перехід на сторінку проектів: {projects_url}"))
                main_app.browser.driver.get(projects_url)
            
            # Парсинг сторінок
            pages_input = self.pages_var.get().strip()
            if not pages_input:
                pages_input = "1-5"
                
            if pages_input.isdigit():
                pages_range = (1, int(pages_input) + 1)
            elif "," in pages_input or "-" in pages_input:
                separator = "," if "," in pages_input else "-"
                n_from, n_to = pages_input.split(separator)
                pages_range = (int(n_from), int(n_to) + 1)
            else:
                pages_range = (1, 6)
                
            self.root.after(0, lambda: self.status_var.set("Парсинг проектів..."))
            self.root.after(0, lambda: self.log_message(f"📄 Парсинг сторінок {pages_range[0]}-{pages_range[1]-1}..."))
            
            for page in range(*pages_range):
                if not self.is_running:
                    break
                self.root.after(0, lambda p=page: self.log_message(f"Парсинг сторінки {p}..."))
                main_app.projects_scraper.save_projects_to_db(page)
                
            if not self.is_running:
                return
                
            # Обробка проектів
            self.root.after(0, lambda: self.status_var.set("Обробка проектів..."))
            self.root.after(0, lambda: self.log_message("🎯 Початок обробки проектів..."))
            
            projects = get_active_projects()
            projects_bid_placed = 0
            projects_skipped = 0
            
            for i, project in enumerate(projects):
                if not self.is_running:
                    break
                    
                self.root.after(0, lambda p=project: self.log_message(f"Обробка: {p.title}"))
                
                try:
                    is_bid_placed = main_app.projects_scraper.parse_project(project)
                    if is_bid_placed:
                        projects_bid_placed += 1
                        self.root.after(0, lambda: self.log_message("✅ Ставку розміщено"))
                    else:
                        projects_skipped += 1
                        self.root.after(0, lambda: self.log_message("⏭️ Проект пропущено"))
                except Exception as e:
                    self.root.after(0, lambda err=e: self.log_message(f"❌ Помилка: {err}"))
                    
            # Завершення
            self.root.after(0, lambda: self.log_message(f"🎉 Завершено! Ставок розміщено: {projects_bid_placed}, Пропущено: {projects_skipped}"))
            self.root.after(0, lambda: self.status_var.set("Автоматизація завершена"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"💥 Критична помилка: {e}"))
            self.root.after(0, lambda: self.status_var.set("Помилка виконання"))
        finally:
            self.root.after(0, self.automation_finished)
            
    def parse_only(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        self.status_var.set("Тільки парсинг...")
        self.log_message("📄 Запуск парсингу...")
        
        # Запускаємо в окремому потоці
        self.automation_thread = threading.Thread(target=self.run_parse_only)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def run_parse_only(self):
        try:
            main_app = Main()
            
            pages_input = self.pages_var.get().strip()
            if not pages_input:
                pages_input = "1-5"
                
            if pages_input.isdigit():
                pages_range = (1, int(pages_input) + 1)
            elif "," in pages_input or "-" in pages_input:
                separator = "," if "," in pages_input else "-"
                n_from, n_to = pages_input.split(separator)
                pages_range = (int(n_from), int(n_to) + 1)
            else:
                pages_range = (1, 6)
                
            for page in range(*pages_range):
                if not self.is_running:
                    break
                self.root.after(0, lambda p=page: self.log_message(f"Парсинг сторінки {p}..."))
                main_app.projects_scraper.save_projects_to_db(page)
                
            self.root.after(0, lambda: self.log_message("✅ Парсинг завершено!"))
            self.root.after(0, lambda: self.status_var.set("Парсинг завершено"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"💥 Помилка парсингу: {e}"))
            self.root.after(0, lambda: self.status_var.set("Помилка парсингу"))
        finally:
            self.root.after(0, self.automation_finished)
            
    def stop_automation(self):
        self.is_running = False
        self.log_message("🛑 Зупинка автоматизації...")
        self.status_var.set("Зупинка...")
        
    def automation_finished(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.refresh_projects()
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def refresh_projects(self):
        # Очищуємо таблицю
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
            
        try:
            projects = get_all_projects()
            
            total_count = len(projects)
            bid_placed_count = sum(1 for p in projects if p.is_bid_placed)
            skipped_count = sum(1 for p in projects if p.is_bid_skipped)
            active_count = total_count - bid_placed_count - skipped_count
            
            self.stats_var.set(f"Всього: {total_count} | Активні: {active_count} | Зі ставками: {bid_placed_count} | Пропущені: {skipped_count}")
            
            for project in projects:
                status = "Зі ставкою" if project.is_bid_placed else ("Пропущений" if project.is_bid_skipped else "Активний")
                
                self.projects_tree.insert("", tk.END, values=(
                    project.id,
                    project.title[:60] + "..." if len(project.title) > 60 else project.title,
                    f"{project.price} UAH" if project.price else "Не вказано",
                    status,
                    "Сьогодні"  # Можна додати реальну дату з бази
                ))
                
        except Exception as e:
            logger.error(f"Помилка оновлення проектів: {e}")
            self.stats_var.set("Помилка завантаження даних")
            
    def filter_projects(self, event=None):
        filter_value = self.filter_var.get()
        
        # Очищуємо таблицю
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
            
        try:
            projects = get_all_projects()
            
            # Фільтруємо проекти
            if filter_value == "Активні":
                projects = [p for p in projects if not p.is_bid_placed and not p.is_bid_skipped]
            elif filter_value == "Зі ставками":
                projects = [p for p in projects if p.is_bid_placed]
            elif filter_value == "Пропущені":
                projects = [p for p in projects if p.is_bid_skipped]
                
            for project in projects:
                status = "Зі ставкою" if project.is_bid_placed else ("Пропущений" if project.is_bid_skipped else "Активний")
                
                self.projects_tree.insert("", tk.END, values=(
                    project.id,
                    project.title[:60] + "..." if len(project.title) > 60 else project.title,
                    f"{project.price} UAH" if project.price else "Не вказано",
                    status,
                    "Сьогодні"
                ))
                
        except Exception as e:
            logger.error(f"Помилка фільтрації проектів: {e}")
            
    def load_log_file(self, event=None):
        log_file = self.log_file_var.get()
        log_path = os.path.join("logs", log_file)
        
        self.log_display.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        
        try:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.log_display.insert(tk.END, content)
            else:
                self.log_display.insert(tk.END, f"Лог файл {log_file} не знайдено")
        except Exception as e:
            self.log_display.insert(tk.END, f"Помилка читання файлу: {e}")
            
        self.log_display.config(state=tk.DISABLED)
        self.log_display.see(tk.END)
        
    def clear_log_file(self):
        log_file = self.log_file_var.get()
        log_path = os.path.join("logs", log_file)
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")
            self.load_log_file()
            messagebox.showinfo("Успіх", f"Лог файл {log_file} очищено!")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося очистити лог файл: {e}")
            
    def get_mfa_code(self):
        """Показує діалог для вводу MFA коду"""
        dialog = MFADialog(self.root)
        return dialog.show()
        
    def _get_mfa_code_from_thread(self):
        """Метод для отримання MFA коду з робочого потоку"""
        self.mfa_code = None
        self.mfa_requested = True
        
        # Показуємо повідомлення в логах
        self.root.after(0, lambda: self.log_message("🔐 Потрібен 2FA код..."))
        
        # Показуємо діалог в головному потоці
        self.root.after(0, self._show_mfa_dialog)
        
        # Чекаємо поки користувач не введе код (або не скасує)
        timeout = 120  # 2 хвилини
        waited = 0
        while self.mfa_requested and waited < timeout:
            import time
            time.sleep(0.5)
            waited += 0.5
            
        return self.mfa_code
        
    def _show_mfa_dialog(self):
        """Показує MFA діалог в головному потоці"""
        code = self.get_mfa_code()
        self.mfa_code = code
        self.mfa_requested = False


def main():
    root = tk.Tk()
    app = FreelancehuntGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
