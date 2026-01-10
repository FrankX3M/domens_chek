# Domain Backlink Analyzer - Makefile

.PHONY: help install setup test test-quick clean lint format

# Переменные
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

help: ## Показать справку
	@echo "Domain Backlink Analyzer - Команды"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

setup: ## Создать структуру проекта
	@chmod +x setup_stage4.sh
	@./setup_stage4.sh
	@echo "✓ Структура создана"
	@echo "  Следующий шаг: скопируйте .env.example в .env и заполните API ключи"

test: ## Запустить все тесты
	$(BIN)/pytest tests/ -v

test-quick: ## Быстрый тест модулей
	$(PYTHON) test_quick.py

test-coverage: ## Тесты с покрытием кода
	$(BIN)/pytest tests/ --cov=src/filtering --cov-report=html --cov-report=term

lint: ## Проверить код (flake8, pylint)
	$(BIN)/flake8 src/ tests/ --max-line-length=100 || true
	$(BIN)/pylint src/ || true

format: ## Форматировать код (black)
	$(BIN)/black src/ tests/ --line-length=100

analyze: ## Запустить анализ (пример)
	$(PYTHON) domain_analyzer.py example.com --limit 1000 --verbose

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	@echo "✓ Временные файлы удалены"

clean-all: clean ## Очистить все (включая venv)
	rm -rf $(VENV)
	@echo "✓ Виртуальное окружение удалено"

env-example: ## Показать пример .env файла
	@cat .env.example

check-env: ## Проверить наличие .env
	@if [ ! -f .env ]; then \
		echo "❌ Файл .env не найден!"; \
		echo "   Скопируйте .env.example в .env и заполните значения"; \
		exit 1; \
	else \
		echo "✓ Файл .env найден"; \
	fi

run-example: check-env ## Запустить пример анализа
	@echo "Запуск примера анализа для example.com..."
	$(PYTHON) domain_analyzer.py example.com --limit 100 --verbose

# Дополнительные команды разработки
dev-install: install ## Установка с dev зависимостями
	$(BIN)/pip install pytest pytest-cov pytest-asyncio black flake8 pylint

watch-tests: ## Запуск тестов при изменении файлов
	$(BIN)/pytest-watch tests/

docs: ## Генерация документации (если настроена)
	@echo "Документация в README.md"
	@cat README.md
