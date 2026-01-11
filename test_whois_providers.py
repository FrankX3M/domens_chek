#!/usr/bin/env python3
"""
Тест различных WHOIS API провайдеров
Проверяет работу всех поддерживаемых сервисов
"""

import asyncio
import os
from dotenv import load_dotenv
from src.availability.whois_checker import WHOISChecker

# Загружаем переменные окружения
load_dotenv()


async def test_provider(provider_name: str, api_key: str, test_domain: str = "google.com"):
    """
    Тест одного провайдера

    Args:
        provider_name: Название провайдера (whoapi, whoxy, whoisxml, apininjas)
        api_key: API ключ
        test_domain: Тестовый домен (по умолчанию google.com - занят)
    """
    print(f"\n{'='*60}")
    print(f"Тестирование провайдера: {provider_name.upper()}")
    print(f"Домен: {test_domain}")
    print(f"{'='*60}")

    try:
        checker = WHOISChecker(
            api_provider=provider_name,
            api_key=api_key,
            timeout=15,
            max_retries=2
        )

        result = await checker.check_domain(test_domain)

        print(f"✓ Результат проверки:")
        print(f"  Домен: {result.domain}")
        print(f"  Статус: {result.status.value}")
        print(f"  Метод: {result.check_method.value}")
        if result.registrar:
            print(f"  Регистратор: {result.registrar}")
        if result.error_message:
            print(f"  Ошибка: {result.error_message}")

        return True

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


async def main():
    """Главная функция тестирования"""

    print("="*60)
    print("WHOIS API Provider Test Suite")
    print("="*60)

    # Получаем настройки из .env
    api_key = os.getenv('WHOIS_API_KEY')
    provider = os.getenv('WHOIS_API_PROVIDER', 'whoapi')

    if not api_key or api_key == 'your_whois_api_key':
        print("\n❌ WHOIS_API_KEY не настроен в .env файле!")
        print("\nИнструкция:")
        print("1. Создайте файл .env на основе .env.example")
        print("2. Зарегистрируйтесь на одном из сервисов:")
        print("   - WhoAPI (10k запросов): https://whoapi.com")
        print("   - Whoxy (250k запросов): https://www.whoxy.com/free-whois-api/")
        print("3. Добавьте ваш API ключ в .env:")
        print("   WHOIS_API_KEY=ваш_ключ")
        print("   WHOIS_API_PROVIDER=whoapi")
        print("\nПодробнее см. WHOIS_API_SETUP.md")
        return

    print(f"\nНастроенный провайдер: {provider}")
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else f"API Key: {api_key}")

    # Тестовые домены
    test_domains = [
        ("google.com", "должен быть REGISTERED"),
        ("thisisverylongunusualdomainname12345.com", "вероятно AVAILABLE")
    ]

    results = []

    for domain, expected in test_domains:
        print(f"\n{'='*60}")
        print(f"Тест: {domain} ({expected})")
        print(f"{'='*60}")

        success = await test_provider(provider, api_key, domain)
        results.append((domain, success))

        # Небольшая пауза между запросами
        await asyncio.sleep(2)

    # Итоговая статистика
    print(f"\n{'='*60}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print(f"{'='*60}")

    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Успешных тестов: {successful}/{total}")

    for domain, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {domain}")

    if successful == total:
        print("\n✓ Все тесты пройдены успешно!")
        print("Ваш WHOIS API настроен правильно и готов к использованию.")
    else:
        print("\n⚠ Некоторые тесты не прошли.")
        print("Проверьте настройки API ключа и лимиты провайдера.")

    print(f"\n{'='*60}")
    print("Готово к использованию:")
    print(f"python domain_analyzer.py example.com --link-type backlinks")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
