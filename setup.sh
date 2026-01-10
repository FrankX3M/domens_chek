#!/bin/bash

# ===================================================================
# Domain Backlink Analyzer - Setup Script
# ===================================================================

set -e  # Exit on error

echo "========================================================================"
echo "  Domain Backlink Analyzer - Установка и настройка"
echo "========================================================================"
echo ""

# Проверка Python версии
echo "[1/5] Проверка Python версии..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Найден Python $python_version"
echo ""

# Создание виртуального окружения
echo "[2/5] Создание виртуального окружения..."
if [ -d "venv" ]; then
    echo "⚠ Виртуальное окружение уже существует, пропуск..."
else
    python3 -m venv venv
    echo "✓ Виртуальное окружение создано"
fi
echo ""

# Активация виртуального окружения
echo "[3/5] Активация виртуального окружения..."
source venv/bin/activate
echo "✓ Виртуальное окружение активировано"
echo ""

# Установка зависимостей
echo "[4/5] Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Зависимости установлены"
echo ""

# Создание .env файла
echo "[5/5] Настройка переменных окружения..."
if [ -f ".env" ]; then
    echo "⚠ Файл .env уже существует, пропуск..."
else
    cp .env.example .env
    echo "✓ Создан файл .env из .env.example"
    echo ""
    echo "⚠ ВАЖНО: Отредактируйте файл .env и укажите ваши API ключи:"
    echo "   - KEYS_SO_API_KEY"
    echo "   - WHOIS_API_KEY"
fi
echo ""

# Создание директории для данных
echo "Создание директории для данных..."
mkdir -p data
echo "✓ Директория data создана"
echo ""

echo "========================================================================"
echo "  ✓ Установка завершена!"
echo "========================================================================"
echo ""
echo "Следующие шаги:"
echo "  1. Активируйте виртуальное окружение:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Отредактируйте файл .env и укажите ваши API ключи:"
echo "     nano .env"
echo ""
echo "  3. Запустите анализ:"
echo "     python domain_analyzer.py example.com"
echo ""
echo "Для получения справки:"
echo "  python domain_analyzer.py --help"
echo ""
