#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест обновленного клиента Keys.so
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Импортируем обновленный клиент
from src.api.keys_so_client import KeysSoClient


async def test_client():
    """Тест обновленного клиента"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    test_domain = "vk.com"

    print("=" * 80)
    print("ТЕСТ ОБНОВЛЕННОГО KEYS.SO CLIENT")
    print("=" * 80)
    print(f"Домен для тестирования: {test_domain}\n")

    async with KeysSoClient(api_key=api_key) as client:

        # 1. Тест get_domain_metrics
        print("1. Получение метрик домена...")
        try:
            metrics = await client.get_domain_metrics(test_domain)
            if metrics:
                print(f"   ✓ SUCCESS")
                print(f"   DR: {metrics.get('dr', 'N/A')}")
                print(f"   Domain: {metrics.get('name', 'N/A')}")
            else:
                print(f"   ✗ FAILED: No metrics returned")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

        await asyncio.sleep(1)

        # 2. Тест get_backlinks_domains
        print("\n2. Получение ссылающихся доменов...")
        try:
            response = await client.get_backlinks_domains(test_domain, per_page=5)
            if response and 'data' in response:
                print(f"   ✓ SUCCESS")
                print(f"   Total domains: {response.get('total', 0)}")
                print(f"   Items on page: {len(response['data'])}")
                if response['data']:
                    first = response['data'][0]
                    print(f"   First domain: {first.get('name', 'N/A')}")
            else:
                print(f"   ✗ FAILED: Invalid response")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

        await asyncio.sleep(1)

        # 3. Тест get_backlinks (ограниченное количество)
        print("\n3. Получение входящих ссылок (первые 10)...")
        try:
            backlinks = await client.get_backlinks(test_domain, limit=10)
            if backlinks:
                print(f"   ✓ SUCCESS")
                print(f"   Got {len(backlinks)} backlinks")
                if backlinks:
                    first = backlinks[0]
                    print(f"   First link from: {first.get('source_name', 'N/A')}")
                    print(f"   Source DR: {first.get('source_dr', 'N/A')}")
            else:
                print(f"   ✗ FAILED: No backlinks returned")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

        await asyncio.sleep(1)

        # 4. Тест get_outlinks_domains
        print("\n4. Получение исходящих доменов...")
        try:
            response = await client.get_outlinks_domains(test_domain, per_page=5)
            if response and 'data' in response:
                print(f"   ✓ SUCCESS")
                print(f"   Total outlink domains: {response.get('total', 0)}")
                print(f"   Items on page: {len(response['data'])}")
                if response['data']:
                    first = response['data'][0]
                    print(f"   First domain: {first.get('name', 'N/A')}")
            else:
                print(f"   ✗ FAILED: Invalid response")
        except Exception as e:
            print(f"   ✗ ERROR: {e}")

    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_client())
