#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест API keys.so без специальных символов
"""

import asyncio
import aiohttp
import os
import json
import sys
from dotenv import load_dotenv

# Настройка кодировки
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def test_api():
    """Простой тест API"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    print("=" * 80)
    print("TEST API KEYS.SO")
    print("=" * 80)

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:

        # 1. domain_dashboard
        print("\n1. Test domain_dashboard (POST):")
        url = "https://api.keys.so/report/simple/domain_dashboard"
        params = {"base": "msk", "domain": "vk.com"}

        try:
            async with session.post(url, json=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS - Keys: {list(data.keys())[:5]}")
                else:
                    text = await response.text()
                    print(f"   FAILED - {text[:200]}")
        except Exception as e:
            print(f"   ERROR: {e}")

        await asyncio.sleep(1)

        # 2. referring_domains с POST
        print("\n2. Test referring_domains (POST):")
        url = "https://api.keys.so/report/simple/links/referring_domains"
        params = {"domain": "vk.com", "base": "msk", "per_page": 10, "page": 1}

        try:
            async with session.post(url, json=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Keys: {list(data.keys())}")
                    if 'data' in data and data['data']:
                        print(f"   Data count: {len(data['data'])}")
                        print(f"   First item keys: {list(data['data'][0].keys())[:5]}")
                else:
                    text = await response.text()
                    print(f"   FAILED - {text}")
        except Exception as e:
            print(f"   ERROR: {e}")

        await asyncio.sleep(1)

        # 3. Пробуем с current_page вместо page
        print("\n3. Test referring_domains with current_page (POST):")
        url = "https://api.keys.so/report/simple/links/referring_domains"
        params = {"domain": "vk.com", "base": "msk", "per_page": 10, "current_page": 1}

        try:
            async with session.post(url, json=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Keys: {list(data.keys())}")
                    if 'data' in data and data['data']:
                        print(f"   Data count: {len(data['data'])}")
                else:
                    text = await response.text()
                    print(f"   FAILED - {text}")
        except Exception as e:
            print(f"   ERROR: {e}")

        await asyncio.sleep(1)

        # 4. incoming links
        print("\n4. Test incoming links (POST):")
        url = "https://api.keys.so/report/simple/links/incoming"
        params = {"domain": "vk.com", "base": "msk", "per_page": 10, "current_page": 1}

        try:
            async with session.post(url, json=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Keys: {list(data.keys())}")
                    if 'data' in data and data['data']:
                        print(f"   Data count: {len(data['data'])}")
                else:
                    text = await response.text()
                    print(f"   FAILED - {text}")
        except Exception as e:
            print(f"   ERROR: {e}")

        await asyncio.sleep(1)

        # 5. Пробуем список из документации JSON
        print("\n5. Reading doc_api_keyso.json for endpoints:")
        try:
            with open('doc_api_keyso.json', 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                print(f"   Doc file loaded successfully")
                if 'paths' in doc_data:
                    print(f"   Found {len(doc_data['paths'])} endpoints in doc")
                    # Ищем endpoint для ссылок
                    for path, methods in doc_data['paths'].items():
                        if 'link' in path.lower() and 'referring' in path.lower():
                            print(f"\n   Found endpoint: {path}")
                            print(f"   Methods: {list(methods.keys())}")
                            if 'post' in methods:
                                post_info = methods['post']
                                if 'parameters' in post_info:
                                    print(f"   Parameters: {[p.get('name') for p in post_info.get('parameters', [])]}")
        except FileNotFoundError:
            print("   Doc file not found")
        except Exception as e:
            print(f"   Error reading doc: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
