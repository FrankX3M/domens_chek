#!/usr/bin/env python3
"""
Поиск рабочих POST эндпоинтов для ссылок
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_endpoints():
    """Тест различных эндпоинтов для ссылок через POST"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    # Пробуем все возможные комбинации эндпоинтов для ссылок
    endpoints = [
        "/report/simple/links/incoming",
        "/report/simple/links/outgoing",
        "/report/simple/links/referring_domains",
        "/report/simple/links/outgoing_domains",
        "/report/simple/links/by_ip",
        "/report/simple/links/anchors",
        "/report/simple/links/popular_pages",
        "/report/simple/links/refdomains",
    ]

    params = {"base": "msk", "domain": "vk.com", "page": 1, "per_page": 10}

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:
        for endpoint in endpoints:
            url = f"https://api.keys.so{endpoint}"

            # Пробуем POST с json параметрами
            try:
                async with session.post(url, json=params) as response:
                    status = response.status
                    text = await response.text()

                    if status == 200:
                        print(f"\n[SUCCESS] POST {endpoint}")
                        import json
                        data = json.loads(text)
                        print(f"  Keys: {list(data.keys())[:10]}")
                        if 'data' in data:
                            print(f"  Data items: {len(data['data'])}")
                            if data['data']:
                                print(f"  First item keys: {list(data['data'][0].keys())}")
                    else:
                        print(f"\n[FAIL] POST {endpoint} - Status: {status}")
                        print(f"  Response: {text[:200]}")
            except Exception as e:
                print(f"\n[ERROR] POST {endpoint} - Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
