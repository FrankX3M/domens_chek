#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования обновленного Keys.so Client

Все методы клиента используют актуальные endpoint'ы API Keys.so
и работают через GET запросы с query параметрами.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.api.keys_so_client import KeysSoClient

load_dotenv()


async def example_1_domain_metrics():
    """Пример 1: Получение метрик домена"""
    print("\n" + "="*60)
    print("ПРИМЕР 1: Получение метрик домена")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    domain = "habr.com"

    async with KeysSoClient(api_key=api_key) as client:
        metrics = await client.get_domain_metrics(domain)

        if metrics:
            print(f"\nДомен: {metrics.get('name')}")
            print(f"DR (Domain Rating): {metrics.get('dr')}")
            print(f"Ссылающихся доменов: {metrics.get('numrefdomains', 'N/A')}")
            print(f"Всего ссылок: {metrics.get('numurl', 'N/A')}")


async def example_2_referring_domains():
    """Пример 2: Получение списка ссылающихся доменов"""
    print("\n" + "="*60)
    print("ПРИМЕР 2: Получение списка ссылающихся доменов")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    domain = "habr.com"

    async with KeysSoClient(api_key=api_key) as client:
        # Получаем первую страницу (25 доменов)
        response = await client.get_backlinks_domains(
            domain=domain,
            per_page=5,  # Для примера берем только 5
            page=1
        )

        print(f"\nВсего ссылающихся доменов: {response.get('total', 0)}")
        print(f"Страница: {response.get('current_page')} из {response.get('last_page')}")
        print("\nПервые 5 доменов:")

        for i, item in enumerate(response.get('data', []), 1):
            print(f"\n{i}. {item.get('name')}")
            print(f"   Ссылок: {item.get('outlinks_count')}")
            print(f"   Активных: {item.get('outlinks_active_count')}")


async def example_3_backlinks_limited():
    """Пример 3: Получение ограниченного количества входящих ссылок"""
    print("\n" + "="*60)
    print("ПРИМЕР 3: Получение входящих ссылок (ограниченное количество)")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    domain = "habr.com"

    async with KeysSoClient(api_key=api_key) as client:
        # Получаем только первые 50 ссылок
        backlinks = await client.get_backlinks(
            domain=domain,
            limit=50
        )

        print(f"\nПолучено ссылок: {len(backlinks)}")
        print("\nПример данных первой ссылки:")

        if backlinks:
            link = backlinks[0]
            print(f"\nИсточник: {link.get('source_name')}")
            print(f"URL источника: {link.get('source_url')}")
            print(f"DR источника: {link.get('source_dr')}")
            print(f"IP источника: {link.get('source_ip')}")
            print(f"Анкор: {link.get('anchor', 'N/A')[:50]}...")
            print(f"Целевой URL: {link.get('url')}")
            print(f"Дата обнаружения: {link.get('created_at')}")
            print(f"Статус: {'Активная' if link.get('status') == 1 else 'Архивная'}")


async def example_4_outlinks():
    """Пример 4: Получение исходящих ссылок"""
    print("\n" + "="*60)
    print("ПРИМЕР 4: Получение исходящих доменов")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    domain = "habr.com"

    async with KeysSoClient(api_key=api_key) as client:
        response = await client.get_outlinks_domains(
            domain=domain,
            per_page=5,
            page=1
        )

        print(f"\nВсего исходящих доменов: {response.get('total', 0)}")
        print("\nПервые 5 доменов:")

        for i, item in enumerate(response.get('data', []), 1):
            print(f"\n{i}. {item.get('name')}")
            print(f"   Обратных ссылок: {item.get('backlinks_count', 'N/A')}")


async def example_5_pagination():
    """Пример 5: Работа с пагинацией"""
    print("\n" + "="*60)
    print("ПРИМЕР 5: Получение данных с пагинацией")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    domain = "habr.com"

    async with KeysSoClient(api_key=api_key) as client:
        all_domains = []
        page = 1
        per_page = 10
        max_domains = 30  # Получим только 30 доменов для примера

        print(f"\nПолучаем до {max_domains} ссылающихся доменов...")

        while len(all_domains) < max_domains:
            response = await client.get_backlinks_domains(
                domain=domain,
                per_page=per_page,
                page=page
            )

            data = response.get('data', [])
            if not data:
                break

            all_domains.extend(data)

            current = response.get('current_page')
            last = response.get('last_page')

            print(f"  Страница {current}/{last} - получено {len(data)} доменов")

            if current >= last or len(all_domains) >= max_domains:
                break

            page += 1
            await asyncio.sleep(0.5)  # Небольшая задержка между запросами

        print(f"\nВсего получено доменов: {len(all_domains[:max_domains])}")


async def example_6_error_handling():
    """Пример 6: Обработка ошибок"""
    print("\n" + "="*60)
    print("ПРИМЕР 6: Обработка ошибок API")
    print("="*60)

    api_key = os.getenv('KEYS_SO_API_KEY')
    invalid_domain = "this-domain-definitely-does-not-exist-12345.com"

    async with KeysSoClient(api_key=api_key) as client:
        try:
            print(f"\nПопытка получить данные для несуществующего домена...")
            metrics = await client.get_domain_metrics(invalid_domain)

            if metrics:
                print(f"Получены данные: {metrics}")
            else:
                print("Данные не получены (домен не найден)")

        except Exception as e:
            print(f"Ошибка: {e}")
            print("Это нормально - домен не существует в базе Keys.so")


async def main():
    """Запуск всех примеров"""
    print("\n" + "="*80)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ KEYS.SO CLIENT")
    print("="*80)

    # Запускаем примеры по очереди
    await example_1_domain_metrics()
    await asyncio.sleep(1)

    await example_2_referring_domains()
    await asyncio.sleep(1)

    await example_3_backlinks_limited()
    await asyncio.sleep(1)

    await example_4_outlinks()
    await asyncio.sleep(1)

    await example_5_pagination()
    await asyncio.sleep(1)

    await example_6_error_handling()

    print("\n" + "="*80)
    print("ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
