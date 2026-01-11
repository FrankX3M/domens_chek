#!/usr/bin/env python3
"""
Тест исправленного API Keys.so
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    """Тест исправленного эндпоинта"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    if not api_key:
        print("KEYS_SO_API_KEY не найден в .env")
        return

    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    # Тестируем правильные эндпоинты с правильными методами
    tests = [
        ("GET", "https://api.keys.so/report/simple/domain_dashboard", {"base": "msk", "domain": "vk.com"}),
        ("GET", "https://api.keys.so/report/simple/links/referring_domains", {"base": "msk", "domain": "vk.com", "page": 1, "per_page": 10}),
    ]

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:
        for method, url, params in tests:
            print(f"\n{'='*70}")
            print(f"Test: {method} {url}")
            print(f"Params: {params}")
            print(f"{'='*70}")

            try:
                if method == "GET":
                    async with session.get(url, params=params) as response:
                        print(f"Status: {response.status}")
                        text = await response.text()
                        if response.status == 200:
                            print(f"SUCCESS! Response length: {len(text)} chars")
                            import json
                            data = json.loads(text)
                            print(f"Data keys: {list(data.keys())}")
                            if 'data' in data:
                                print(f"Data items: {len(data['data'])}")
                        else:
                            print(f"Response: {text[:500]}")

            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
