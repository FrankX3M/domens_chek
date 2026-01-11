#!/usr/bin/env python3
"""
Поиск рабочих эндпоинтов для ссылок
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_endpoints():
    """Тест различных эндпоинтов для ссылок"""

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
        "/report/simple/links/ip_subnets",
        "/report/simple/links/anchors",
        "/report/simple/links/popular_pages",
        "/report/simple/links/refdomains",
        "/links/referring_domains",
        "/links/refdomains",
    ]

    params = {"base": "msk", "domain": "vk.com", "page": 1, "per_page": 10}

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:
        for endpoint in endpoints:
            url = f"https://api.keys.so{endpoint}"

            # Пробуем GET
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        print(f"✓ SUCCESS GET {endpoint}")
                        text = await response.text()
                        import json
                        data = json.loads(text)
                        print(f"  Keys: {list(data.keys())[:5]}")
                        if 'data' in data:
                            print(f"  Data items: {len(data['data'])}")
                    elif response.status != 400 and response.status != 404:
                        print(f"? GET {endpoint} - Status: {response.status}")
            except Exception as e:
                pass

if __name__ == "__main__":
    asyncio.run(test_endpoints())
