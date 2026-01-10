#!/usr/bin/env python3
"""
Скрипт для создания структуры проекта Domain Backlink Analyzer
Автоматически создает все необходимые директории и файлы
"""

import os
from pathlib import Path


def create_project_structure():
    """Создание полной структуры проекта"""
    
    print("🚀 Создание структуры проекта Domain Backlink Analyzer...")
    print("=" * 70)
    
    # Базовая директория проекта
    base_dir = Path(__file__).parent
    
    # Список директорий для создания
    directories = [
        "src",
        "src/api",
        "src/models",
        "src/domain",
        "src/availability",
        "src/filtering",
        "src/export",
        "src/utils",
        "data",
        "output",
        "tests",
        "tests/unit",
        "tests/integration",
        "logs",
    ]
    
    # Создание директорий
    print("\n📁 Создание директорий:")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    # Создание __init__.py файлов
    print("\n📝 Создание __init__.py файлов:")
    init_files = [
        "src/__init__.py",
        "src/api/__init__.py",
        "src/models/__init__.py",
        "src/domain/__init__.py",
        "src/availability/__init__.py",
        "src/filtering/__init__.py",
        "src/export/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
    ]
    
    for init_file in init_files:
        file_path = base_dir / init_file
        if not file_path.exists():
            file_path.touch()
            print(f"  ✓ {init_file}")
    
    # Создание файлов данных
    print("\n📄 Создание файлов данных:")
    
    # spam_phrases.txt
    spam_file = base_dir / "data" / "spam_phrases.txt"
    if not spam_file.exists():
        spam_file.write_text("""# Спам-фразы для фильтрации анкоров (по одной на строку)
casino
viagra
porn
xxx
gambling
pills
poker
betting
""", encoding='utf-8')
        print(f"  ✓ data/spam_phrases.txt")
    
    # excluded_domains.txt
    excluded_file = base_dir / "data" / "excluded_domains.txt"
    if not excluded_file.exists():
        excluded_file.write_text("""# Исключенные домены (по одному на строку)
facebook.com
twitter.com
youtube.com
google.com
linkedin.com
instagram.com
pinterest.com
reddit.com
medium.com
wikipedia.org
""", encoding='utf-8')
        print(f"  ✓ data/excluded_domains.txt")
    
    # .env.example
    env_example = base_dir / ".env.example"
    if not env_example.exists():
        env_example.write_text("""# Keys.so API
KEYS_SO_API_KEY=your_api_key_here
KEYS_SO_BASE_URL=https://api.keys.so/v1

# WHOIS API (опционально)
WHOIS_API_KEY=your_whois_api_key
WHOIS_API_PROVIDER=whoisxml

# Настройки
LOG_LEVEL=INFO
LOG_FILE=logs/analyzer.log
MAX_CONCURRENT_REQUESTS=20
REQUEST_TIMEOUT=30
MAX_RETRIES=3
""", encoding='utf-8')
        print(f"  ✓ .env.example")
    
    # .gitignore
    gitignore = base_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env

# Logs
logs/
*.log

# Output files
output/
*.csv
*.xlsx
*.json

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
""", encoding='utf-8')
        print(f"  ✓ .gitignore")
    
    # README.md
    readme = base_dir / "README.md"
    if not readme.exists():
        readme.write_text("""# Domain Backlink Analyzer

Инструмент для анализа обратных ссылок домена с фильтрацией, проверкой доступности и экспортом результатов.

## Установка

```bash
# Клонировать репозиторий
git clone <repo-url>
cd domain-backlink-analyzer

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\\Scripts\\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env и добавить API ключи
```

## Использование

```bash
# Базовый анализ
python domain_analyzer.py example.com

# С экспортом в Excel
python domain_analyzer.py example.com -f xlsx -o report.xlsx

# Полный анализ с подробным логированием
python domain_analyzer.py example.com --verbose --include-spam

# Помощь
python domain_analyzer.py --help
```

## Структура проекта

```
domain-backlink-analyzer/
├── src/
│   ├── api/              # API клиенты
│   ├── models/           # Модели данных
│   ├── domain/           # Извлечение доменов
│   ├── availability/     # Проверка доступности
│   ├── filtering/        # Фильтрация и метрики
│   ├── export/           # Экспорт результатов
│   └── utils/            # Утилиты
├── data/                 # Конфигурационные файлы
├── output/               # Результаты анализа
├── tests/                # Тесты
└── domain_analyzer.py    # Главный скрипт
```

## Возможности

- ✅ Сбор обратных ссылок через Keys.so API
- ✅ Извлечение уникальных доменов
- ✅ Проверка доступности доменов (RDAP/WHOIS)
- ✅ Фильтрация спама по анкорам
- ✅ Исключение нежелательных доменов
- ✅ Сбор метрик (DR, UR, трафик)
- ✅ Экспорт в CSV, Excel, JSON

## Лицензия

MIT
""", encoding='utf-8')
        print(f"  ✓ README.md")
    
    print("\n" + "=" * 70)
    print("✅ Структура проекта создана успешно!")
    print("\nСледующие шаги:")
    print("  1. Установите зависимости: pip install -r requirements.txt")
    print("  2. Скопируйте .env.example в .env и настройте API ключи")
    print("  3. Запустите анализ: python domain_analyzer.py example.com")
    print("=" * 70)


if __name__ == "__main__":
    create_project_structure()
