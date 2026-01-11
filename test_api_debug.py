#!/usr/bin/env python3
"""
Отладка API Keys.so
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    """Тест различных эндпоинтов API"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    if not api_key:
        print("KEYS_SO_API_KEY не найден в .env")
        return

    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    # Попробуем разные эндпоинты и методы
    tests = [
        ("GET", "https://api.keys.so/report/simple/domain_dashboard", {"base": "msk", "domain": "vk.com"}),
        ("POST", "https://api.keys.so/report/simple/domain_dashboard", {"base": "msk", "domain": "vk.com"}),
        ("GET", "https://api.keys.so/report/simple/links/refdomains", {"base": "msk", "domain": "vk.com", "page": 1, "per_page": 10}),
        ("POST", "https://api.keys.so/report/simple/links/refdomains", {"base": "msk", "domain": "vk.com", "page": 1, "per_page": 10}),
    ]

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:
        for method, url, params in tests:
            print(f"\n{'='*70}")
            print(f"Тест: {method} {url}")
            print(f"Параметры: {params}")
            print(f"{'='*70}")

            try:
                if method == "GET":
                    async with session.get(url, params=params) as response:
                        print(f"Статус: {response.status}")
                        print(f"Заголовки: {dict(response.headers)}")
                        text = await response.text()
                        print(f"Ответ: {text[:500]}")
                else:
                    async with session.post(url, json=params) as response:
                        print(f"Статус: {response.status}")
                        print(f"Заголовки: {dict(response.headers)}")
                        text = await response.text()
                        print(f"Ответ: {text[:500]}")

                if response.status == 200:
                    print("\n✓ УСПЕХ!")
                    break

            except Exception as e:
                print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
