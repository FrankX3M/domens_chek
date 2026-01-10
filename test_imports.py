#!/usr/bin/env python3
"""
Тест импортов всех модулей
Проверка, что все модули правильно импортируются
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Тестирование импортов всех модулей"""
    
    print("🔍 Проверка импортов модулей...")
    print("=" * 70)
    
    errors = []
    
    # Тест 1: API Client
    try:
        from src.api.keys_so_client import KeysSoClient
        print("✓ src.api.keys_so_client - OK")
    except Exception as e:
        errors.append(f"✗ src.api.keys_so_client: {e}")
        print(f"✗ src.api.keys_so_client - FAILED: {e}")
    
    # Тест 2: Models
    try:
        from src.models.filtered_domain import FilteredDomain
        print("✓ src.models.filtered_domain - OK")
    except Exception as e:
        errors.append(f"✗ src.models.filtered_domain: {e}")
        print(f"✗ src.models.filtered_domain - FAILED: {e}")
    
    # Тест 3: Domain Extractor
    try:
        from src.domain.extractor import DomainExtractor
        print("✓ src.domain.extractor - OK")
    except Exception as e:
        errors.append(f"✗ src.domain.extractor: {e}")
        print(f"✗ src.domain.extractor - FAILED: {e}")
    
    # Тест 4: Availability Checker
    try:
        from src.availability import DomainAvailabilityChecker, AvailabilityResult, DomainStatus
        print("✓ src.availability - OK")
    except Exception as e:
        errors.append(f"✗ src.availability: {e}")
        print(f"✗ src.availability - FAILED: {e}")
    
    # Тест 5: Filtering Pipeline
    try:
        from src.filtering import DomainFilteringPipeline
        print("✓ src.filtering - OK")
    except Exception as e:
        errors.append(f"✗ src.filtering: {e}")
        print(f"✗ src.filtering - FAILED: {e}")
    
    # Тест 6: Exporters
    try:
        from src.export.csv_exporter import CSVExporter
        from src.export.json_exporter import JSONExporter
        print("✓ src.export.csv_exporter - OK")
        print("✓ src.export.json_exporter - OK")
    except Exception as e:
        errors.append(f"✗ src.export: {e}")
        print(f"✗ src.export - FAILED: {e}")
    
    # Тест 7: Excel Exporter (может не быть openpyxl)
    try:
        from src.export.excel_exporter import ExcelExporter
        print("✓ src.export.excel_exporter - OK")
    except ImportError:
        print("⚠ src.export.excel_exporter - SKIP (openpyxl не установлен)")
    except Exception as e:
        errors.append(f"✗ src.export.excel_exporter: {e}")
        print(f"✗ src.export.excel_exporter - FAILED: {e}")
    
    # Тест 8: Utils
    try:
        from src.utils.config import APIConfig, LogConfig, AppConfig
        from src.utils.logger import setup_logger, get_logger
        print("✓ src.utils.config - OK")
        print("✓ src.utils.logger - OK")
    except Exception as e:
        errors.append(f"✗ src.utils: {e}")
        print(f"✗ src.utils - FAILED: {e}")
    
    print("=" * 70)
    
    if errors:
        print(f"\n❌ Тест провален! Обнаружено ошибок: {len(errors)}\n")
        for error in errors:
            print(f"  • {error}")
        return False
    else:
        print("\n✅ Все модули импортируются корректно!")
        print("\nСледующие шаги:")
        print("  1. Установите зависимости: pip install -r requirements.txt")
        print("  2. Настройте .env файл с API ключами")
        print("  3. Запустите: python domain_analyzer.py --help")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
