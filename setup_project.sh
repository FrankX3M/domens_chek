#!/bin/bash

# ============================================================================
# Domain Backlink Analyzer - Скрипт создания структуры проекта (Этап 2)
# ============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода цветных сообщений
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo ""
}

# Начало
print_header "СОЗДАНИЕ СТРУКТУРЫ ПРОЕКТА - ЭТАП 2"

# Проверка, что скрипт запущен из правильной директории
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
print_info "Рабочая директория: $SCRIPT_DIR"

# Имя проекта
PROJECT_NAME="domain-backlink-analyzer"
print_info "Имя проекта: $PROJECT_NAME"

# Создание корневой директории проекта
print_info "Создание корневой директории..."
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"
print_success "Корневая директория создана"

# Создание структуры директорий
print_info "Создание структуры директорий..."

# Основные директории
mkdir -p src/domain
mkdir -p src/models
mkdir -p src/api
mkdir -p src/utils
mkdir -p tests/test_domain
mkdir -p data/cache
mkdir -p logs
mkdir -p .tld_cache

print_success "Структура директорий создана"

# Создание __init__.py файлов
print_info "Создание __init__.py файлов..."

touch src/__init__.py
touch src/domain/__init__.py
touch src/models/__init__.py
touch src/api/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/test_domain/__init__.py

print_success "Файлы __init__.py созданы"

# Копирование файлов из рабочей директории
print_info "Копирование файлов проекта..."

# Модели
if [ -f "$SCRIPT_DIR/domain_info.py" ]; then
    cp "$SCRIPT_DIR/domain_info.py" src/models/domain_info.py
    print_success "  src/models/domain_info.py"
fi

# Модуль domain
if [ -f "$SCRIPT_DIR/normalizer.py" ]; then
    cp "$SCRIPT_DIR/normalizer.py" src/domain/normalizer.py
    print_success "  src/domain/normalizer.py"
fi

if [ -f "$SCRIPT_DIR/extractor.py" ]; then
    cp "$SCRIPT_DIR/extractor.py" src/domain/extractor.py
    print_success "  src/domain/extractor.py"
fi

if [ -f "$SCRIPT_DIR/domain__init__.py" ]; then
    cp "$SCRIPT_DIR/domain__init__.py" src/domain/__init__.py
    print_success "  src/domain/__init__.py"
fi

# Тесты
if [ -f "$SCRIPT_DIR/test_extractor.py" ]; then
    cp "$SCRIPT_DIR/test_extractor.py" tests/test_domain/test_extractor.py
    print_success "  tests/test_domain/test_extractor.py"
fi

if [ -f "$SCRIPT_DIR/test_normalizer.py" ]; then
    cp "$SCRIPT_DIR/test_normalizer.py" tests/test_domain/test_normalizer.py
    print_success "  tests/test_domain/test_normalizer.py"
fi

# Конфигурация
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    cp "$SCRIPT_DIR/requirements.txt" requirements.txt
    print_success "  requirements.txt"
fi

# Демо-скрипт
if [ -f "$SCRIPT_DIR/demo_stage2.py" ]; then
    cp "$SCRIPT_DIR/demo_stage2.py" demo_stage2.py
    chmod +x demo_stage2.py
    print_success "  demo_stage2.py"
fi

# Создание .env.example
print_info "Создание .env.example..."
cat > .env.example << 'EOF'
# API Configuration
API_KEY=your_keys_so_api_key_here
API_BASE_URL=https://api.keys.so/v1
API_TIMEOUT=30
API_MAX_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/domain_analyzer.log
EOF
print_success ".env.example создан"

# Создание .gitignore
print_info "Создание .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env

# Logs
logs/
*.log

# Cache
.tld_cache/
data/cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Project specific
*.csv
*.xlsx
*.json
!config/*.json
EOF
print_success ".gitignore создан"

# Создание README.md
print_info "Создание README.md..."
cat > README.md << 'EOF'
# Domain Backlink Analyzer - Этап 2

Анализатор обратных ссылок с обработкой и нормализацией доменов.

## Реализованные этапы

### ✅ Этап 1: Сбор обратных ссылок
- Интеграция с Keys.so API
- Асинхронная загрузка данных
- Обработка ошибок и повторные попытки

### ✅ Этап 2: Обработка и нормализация доменов
- Извлечение уникальных корневых доменов
- Удаление поддоменов (blog.example.com → example.com)
- Нормализация www
- Обработка доменов второго уровня (.co.uk, .com.au)
- Удаление дубликатов

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения:
   ```bash
   cp .env.example .env
   # Отредактируйте .env и добавьте свой API ключ
   ```

## Использование

### Демонстрация Этапа 2
```bash
python demo_stage2.py
```

### Запуск тестов
```bash
# Все тесты
pytest

# Конкретный модуль
python tests/test_domain/test_extractor.py
python tests/test_domain/test_normalizer.py
```

## Структура проекта

```
domain-backlink-analyzer/
├── src/
│   ├── domain/              # Обработка доменов (Этап 2)
│   │   ├── __init__.py
│   │   ├── normalizer.py    # Нормализация доменов
│   │   └── extractor.py     # Извлечение корневых доменов
│   │
│   ├── models/              # Модели данных
│   │   └── domain_info.py   # Модель обработанного домена
│   │
│   ├── api/                 # API клиенты (Этап 1)
│   ├── utils/               # Утилиты
│   └── __init__.py
│
├── tests/                   # Тесты
│   └── test_domain/
│       ├── test_extractor.py
│       └── test_normalizer.py
│
├── logs/                    # Логи
├── data/                    # Данные
├── requirements.txt         # Зависимости
├── .env.example            # Пример конфигурации
└── README.md               # Документация
```

## Примеры использования

### Извлечение корневых доменов
```python
from src.domain.extractor import DomainExtractor

extractor = DomainExtractor()

# Извлечение корневого домена
root = extractor.get_root_domain("blog.example.com")
# Результат: "example.com"

# Извлечение уникальных доменов из списка backlinks
unique_domains = extractor.extract_unique_domains(backlinks)
```

### Нормализация доменов
```python
from src.domain.normalizer import DomainNormalizer

# Полная нормализация
normalized = DomainNormalizer.normalize("HTTPS://WWW.EXAMPLE.COM/PATH")
# Результат: "example.com"

# Проверка валидности
is_valid = DomainNormalizer.is_valid_domain("example.com")
# Результат: True
```

## Следующие этапы

- [ ] Этап 3: Проверка регистрации доменов
- [ ] Этап 4: Спам-фильтр
- [ ] Этап 5: Экспорт результатов

## Лицензия

MIT
EOF
print_success "README.md создан"

# Финальное сообщение
print_header "СТРУКТУРА ПРОЕКТА УСПЕШНО СОЗДАНА!"

print_info "Следующие шаги:"
echo "  1. cd $PROJECT_NAME"
echo "  2. python -m venv venv"
echo "  3. source venv/bin/activate  # или venv\\Scripts\\activate на Windows"
echo "  4. pip install -r requirements.txt"
echo "  5. cp .env.example .env"
echo "  6. # Отредактируйте .env и добавьте API ключ"
echo "  7. python demo_stage2.py  # Запуск демонстрации"
echo ""

print_success "Готово! Проект настроен и готов к использованию."
