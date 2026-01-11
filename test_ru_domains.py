#!/usr/bin/env python3
"""
Тест проверки .ru доменов через Whoxy API
Проверяет 10-15 случайных .ru доменов с детальным логированием
"""

import asyncio
import os
from dotenv import load_dotenv
from src.availability.checker import DomainAvailabilityChecker

# Загружаем переменные окружения
load_dotenv()


async def main():
    """Тест проверки .ru доменов"""

    print("="*70)
    print("Test .ru domains check via Whoxy API")
    print("="*70)

    # Проверяем настройки
    api_key = os.getenv('WHOIS_API_KEY')
    provider = os.getenv('WHOIS_API_PROVIDER', 'whoxy')

    if not api_key or api_key == 'your_whois_api_key':
        print("\n[ERROR] WHOIS_API_KEY not configured!")
        print("Add to .env file:")
        print("WHOIS_API_KEY=your_whoxy_key")
        print("WHOIS_API_PROVIDER=whoxy")
        return

    print(f"\nProvider: {provider}")
    print(f"API Key: {api_key[:15]}..." if len(api_key) > 15 else f"API Key: {api_key}")

    # Test .ru domains (mix of known and potentially available)
    test_domains = [
        # Known registered
        "yandex.ru",
        "mail.ru",
        "vk.ru",

        # Potentially available (random combinations)
        "testdomain12345xyz.ru",
        "randomsite9876543.ru",
        "unusualname2026test.ru",
        "verylongdomainname123456789.ru",
        "xyz123test456.ru",

        # Short (might be registered)
        "test123.ru",
        "abc456.ru",

        # Medium length
        "mywebsite2026.ru",
        "bestservice24.ru",
        "newproject2026.ru",
        "example-test-site.ru"
    ]

    print(f"\nWill check {len(test_domains)} domains")
    print("="*70)

    # Создаем checker
    checker = DomainAvailabilityChecker(
        whois_api_key=api_key,
        whois_provider=provider,
        max_concurrent=5,  # Уменьшаем для более детального вывода
        skip_rdap=False    # Пробуем сначала RDAP, потом WHOIS
    )

    # Проверяем домены по одному для детального вывода
    results = []
    available_count = 0
    registered_count = 0
    error_count = 0

    for i, domain in enumerate(test_domains, 1):
        print(f"\n[{i}/{len(test_domains)}] Проверка: {domain}")
        print("-" * 70)

        result = await checker.check_domain(domain)
        results.append(result)

        # Статистика
        if result.status.value == "AVAILABLE":
            available_count += 1
            status_emoji = "[AVAILABLE]"
        elif result.status.value == "REGISTERED":
            registered_count += 1
            status_emoji = "[REGISTERED]"
        else:
            error_count += 1
            status_emoji = "[ERROR]"

        print(f"  Status: {status_emoji}")
        print(f"  Check method: {result.checked_via}")
        if result.error:
            print(f"  Error: {result.error}")

        # Небольшая пауза между запросами
        if i < len(test_domains):
            await asyncio.sleep(0.5)

    # Final statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total checked: {len(results)}")
    print(f"  - Available: {available_count}")
    print(f"  - Registered: {registered_count}")
    print(f"  - Errors: {error_count}")

    # Check methods details
    print("\nCheck methods used:")
    methods = {}
    for r in results:
        methods[r.checked_via] = methods.get(r.checked_via, 0) + 1

    for method, count in methods.items():
        print(f"  - {method}: {count}")

    # Список свободных доменов
    if available_count > 0:
        print("\n" + "="*70)
        print("AVAILABLE DOMAINS:")
        print("="*70)
        for r in results:
            if r.status.value == "AVAILABLE":
                print(f"  [+] {r.domain} (checked via {r.checked_via})")
    else:
        print("\n[!] No available domains found")
        print("This is normal if all test domains are registered")

    # Список ошибок
    if error_count > 0:
        print("\n" + "="*70)
        print("CHECK ERRORS:")
        print("="*70)
        for r in results:
            if r.status.value not in ["AVAILABLE", "REGISTERED"]:
                print(f"  [!] {r.domain}: {r.error}")

    print("\n" + "="*70)

    # Проверка использования Whoxy
    whoxy_used = any(r.checked_via == "whois" for r in results)
    if whoxy_used:
        print("[OK] Whoxy API is being used for domain checks")
    else:
        print("[!] Whoxy API was not used")
        print("  Possibly all domains were checked via RDAP")
        print("  Try running with --skip-rdap to force WHOIS usage")

    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
