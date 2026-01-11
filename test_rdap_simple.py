#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест RDAP проверки доступности доменов
"""

import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from src.availability.checker import DomainAvailabilityChecker


async def test_rdap():
    """Тест RDAP проверки"""

    # Тестовые домены
    test_domains = [
        "google.com",  # точно занят
        "wikipedia.org",  # точно занят
        "verylongunusualdomainname123456789test.com",  # скорее всего свободен
    ]

    print("=" * 80)
    print("ТЕСТ RDAP ПРОВЕРКИ ДОСТУПНОСТИ")
    print("=" * 80)

    # Создаем checker без WHOIS API (только RDAP)
    checker = DomainAvailabilityChecker(
        whois_api_key=None,
        skip_rdap=False,
        max_concurrent=5
    )

    print("\nПроверка доменов...")
    results = await checker.check_domains(test_domains)

    print("\nРезультаты:")
    print("-" * 80)

    for result in results:
        status_icon = "✅" if result.status.value == "AVAILABLE" else "❌" if result.status.value == "REGISTERED" else "❓"
        print(f"{status_icon} {result.domain:50} | {result.status.value:12} | via: {result.checked_via}")
        if result.error:
            print(f"   Ошибка: {result.error}")

    # Статистика
    available = sum(1 for r in results if r.status.value == "AVAILABLE")
    registered = sum(1 for r in results if r.status.value == "REGISTERED")
    errors = sum(1 for r in results if r.status.value == "ERROR")

    print("\n" + "=" * 80)
    print(f"Свободных: {available} | Зарегистрированных: {registered} | Ошибок: {errors}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_rdap())
