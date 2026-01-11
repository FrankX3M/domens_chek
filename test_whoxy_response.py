#!/usr/bin/env python3
"""
Тест ответа Whoxy API
Показывает реальный ответ от API для понимания формата
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()


async def test_whoxy_response():
    """Тестируем ответ Whoxy API"""

    api_key = os.getenv('WHOIS_API_KEY')

    if not api_key or api_key == 'your_whois_api_key':
        print("[ERROR] WHOIS_API_KEY not configured in .env")
        return

    print("="*70)
    print("Whoxy API Response Test")
    print("="*70)
    print(f"API Key: {api_key[:15]}...")

    # Тестовые домены
    test_domains = [
        "google.com",     # Точно зарегистрирован
        "yandex.ru",      # Точно зарегистрирован
        "thisisverylongunusualdomainname12345.com"  # Вероятно свободен
    ]

    for domain in test_domains:
        print(f"\n{'='*70}")
        print(f"Testing: {domain}")
        print(f"{'='*70}")

        url = "https://api.whoxy.com/"
        params = {
            "key": api_key,
            "whois": domain
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    print(f"HTTP Status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print("\nJSON Response:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))

                        # Анализируем поля
                        print("\nKey fields:")
                        print(f"  - status: {data.get('status')}")
                        print(f"  - domain_registered: {data.get('domain_registered')}")
                        print(f"  - domain_name: {data.get('domain_name')}")
                        print(f"  - registrar_name: {data.get('registrar_name')}")
                        print(f"  - create_date: {data.get('create_date')}")
                    else:
                        text = await response.text()
                        print(f"Error response: {text}")

        except Exception as e:
            print(f"Exception: {e}")

        await asyncio.sleep(2)  # Пауза между запросами

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(test_whoxy_response())
