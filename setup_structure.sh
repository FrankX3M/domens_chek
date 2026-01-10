#!/bin/bash

# Скрипт для создания структуры проекта Domain Backlink Analyzer - Этап 1

echo "🚀 Создание структуры проекта Domain Backlink Analyzer - Этап 1..."

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p src/api
mkdir -p src/models
mkdir -p src/utils
mkdir -p tests/test_api

# Создание __init__.py файлов
echo "📝 Создание __init__.py файлов..."
touch src/__init__.py
touch src/api/__init__.py
touch src/models/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/test_api/__init__.py

echo "✅ Структура проекта создана успешно!"
echo ""
echo "📋 Структура проекта:"
tree -I '__pycache__|*.pyc|.pytest_cache' || ls -R

echo ""
echo "📖 Следующие шаги:"
echo "1. Скопируйте .env.example в .env и добавьте ваш API ключ"
echo "2. Установите зависимости: pip install -r requirements.txt"
echo "3. Запустите анализатор: python domain_analyzer.py example.com"
