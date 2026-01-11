#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправленного DomainExtractor с реальными данными API
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Настройка кодировки
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from src.api.keys_so_client import KeysSoClient
from src.domain.extractor import DomainExtractor


async def test_extractor():
    """Тест экстрактора с реальными данными"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    test_domain = "habr.com"

    print("="*80)
    print("ТЕСТ DOMAIN EXTRACTOR С РЕАЛЬНЫМИ ДАННЫМИ")
    print("="*80)
    print(f"Тестовый домен: {test_domain}\n")

    async with KeysSoClient(api_key=api_key) as client:

        # Получаем небольшое количество backlinks для теста
        print("1. Получение backlinks от API...")
        backlinks = await client.get_backlinks(test_domain, limit=100)
        print(f"   Получено backlinks: {len(backlinks)}")

        # Показываем структуру первой ссылки
        if backlinks:
            print("\n2. Структура первого backlink:")
            first = backlinks[0]
            print(f"   Keys: {list(first.keys())}")
            print(f"   source_name: {first.get('source_name')}")
            print(f"   source_dr: {first.get('source_dr')}")
            print(f"   anchor: {first.get('anchor', 'N/A')[:50]}")

        # Тестируем экстрактор
        print("\n3. Извлечение уникальных доменов...")
        extractor = DomainExtractor()
        unique_domains = extractor.extract_unique_domains(backlinks)

        print(f"   Уникальных доменов найдено: {len(unique_domains)}")

        if unique_domains:
            print("\n4. Первые 10 уникальных доменов:")
            for i, domain in enumerate(unique_domains[:10], 1):
                print(f"   {i}. {domain}")
        else:
            print("\n   ОШИБКА: Не найдено ни одного домена!")

        # Проверка соотношения
        if len(backlinks) > 0:
            ratio = len(unique_domains) / len(backlinks) * 100
            print(f"\n5. Статистика:")
            print(f"   Backlinks: {len(backlinks)}")
            print(f"   Уникальных доменов: {len(unique_domains)}")
            print(f"   Уникальность: {ratio:.1f}%")

    print("\n" + "="*80)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_extractor())
