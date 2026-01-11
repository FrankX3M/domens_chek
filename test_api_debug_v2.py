#!/usr/bin/env python3
"""
Подробная отладка API keys.so
"""

import asyncio
import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_debug():
    """Детальная проверка работы API"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    print("="*80)
    print("ОТЛАДКА API KEYS.SO")
    print("="*80)

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:

        # 1. Проверяем domain_dashboard (который работал раньше)
        print("\n1. Тест domain_dashboard (POST):")
        url = "https://api.keys.so/report/simple/domain_dashboard"
        params = {"base": "msk", "domain": "vk.com"}

        try:
            async with session.post(url, json=params) as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ SUCCESS - Keys: {list(data.keys())}")
                else:
                    text = await response.text()
                    print(f"   ✗ FAILED - {text[:200]}")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

        await asyncio.sleep(1)

        # 2. Пробуем referring_domains с разными методами
        print("\n2. Тест referring_domains (OPTIONS):")
        url = "https://api.keys.so/report/simple/links/referring_domains"

        try:
            async with session.options(url) as response:
                print(f"   Статус: {response.status}")
                print(f"   Headers: {dict(response.headers)}")
                if response.status in [200, 204]:
                    print(f"   ✓ OPTIONS работает")
                else:
                    text = await response.text()
                    print(f"   Response: {text[:200]}")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

        await asyncio.sleep(1)

        # 3. Пробуем альтернативные endpoint'ы из старого кода
        print("\n3. Тест альтернативных endpoint'ов:")

        alternatives = [
            "/report/simple/links/refdomains",
            "/report/backlinks",
            "/backlinks",
            "/api/backlinks",
            "/v1/backlinks",
        ]

        for endpoint in alternatives:
            url = f"https://api.keys.so{endpoint}"
            try:
                async with session.post(url, json={"domain": "vk.com", "base": "msk"}) as response:
                    if response.status == 200:
                        print(f"   ✓ {endpoint} - SUCCESS (POST)")
                        data = await response.json()
                        print(f"     Keys: {list(data.keys())}")
                        break
                    elif response.status != 404:
                        print(f"   ? {endpoint} - Status: {response.status}")
            except Exception as e:
                pass

            await asyncio.sleep(0.5)

        # 4. Проверяем, что именно передавать в referring_domains
        print("\n4. Тест referring_domains с разными форматами параметров:")
        url = "https://api.keys.so/report/simple/links/referring_domains"

        param_variants = [
            {"domain": "vk.com", "base": "msk", "per_page": 10, "page": 1},
            {"domain": "vk.com", "base": "msk", "current_page": 1, "per_page": 10},
            {"domain": "vk.com", "base": "msk"},
            {"domain": "vk.com"},
        ]

        for i, params in enumerate(param_variants, 1):
            print(f"\n   Вариант {i}: {params}")
            try:
                async with session.post(url, json=params) as response:
                    print(f"   Статус: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✓ SUCCESS")
                        print(f"   Keys: {list(data.keys())}")
                        if 'data' in data:
                            print(f"   Data count: {len(data['data'])}")
                        break
                    else:
                        text = await response.text()
                        print(f"   Error: {text[:150]}")
            except Exception as e:
                print(f"   Exception: {e}")

            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_debug())
