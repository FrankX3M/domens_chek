#!/bin/bash

# Скрипт для создания структуры проекта Этапа 4
# Domain Backlink Analyzer

echo "🚀 Создание структуры проекта для Этапа 4..."

# Создаем директории
echo "📁 Создание директорий..."
mkdir -p src/filtering
mkdir -p src/models
mkdir -p data
mkdir -p tests/test_filtering

# Создаем пустые __init__.py файлы
echo "📄 Создание __init__.py файлов..."
touch src/filtering/__init__.py
touch tests/test_filtering/__init__.py

# Создаем файлы данных
echo "📋 Создание файлов данных..."
touch data/spam_phrases.txt
touch data/excluded_domains.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "🔧 Создание .env файла..."
    cat > .env << 'EOF'
# API Configuration
API_KEY=your_keys_so_api_key_here
API_BASE_URL=https://api.keys.so/v1
WHOIS_API_KEY=your_whois_api_key_here

# Фильтрация
SPAM_PHRASES_FILE=data/spam_phrases.txt
EXCLUDED_DOMAINS_FILE=data/excluded_domains.txt
ENABLE_SPAM_FILTER=true

# Сбор метрик
FETCH_DOMAIN_METRICS=true
MAX_CONCURRENT_METRICS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/domain_analyzer.log
EOF
    echo "✓ .env файл создан (не забудьте добавить API ключи)"
else
    echo "ℹ️  .env файл уже существует, пропускаем"
fi

# Устанавливаем права на выполнение для скрипта
chmod +x setup_stage4.sh

echo ""
echo "✅ Структура проекта создана успешно!"
echo ""
echo "📂 Созданные директории:"
echo "   src/filtering/"
echo "   tests/test_filtering/"
echo ""
echo "📄 Созданные файлы конфигурации:"
echo "   data/spam_phrases.txt"
echo "   data/excluded_domains.txt"
echo "   .env (если не существовал)"
echo ""
echo "🔜 Следующие шаги:"
echo "   1. Заполните API ключи в .env файле"
echo "   2. Добавьте спам-фразы в data/spam_phrases.txt"
echo "   3. (Опционально) Добавьте исключения в data/excluded_domains.txt"
echo "   4. Запустите тесты: pytest tests/"
echo ""
