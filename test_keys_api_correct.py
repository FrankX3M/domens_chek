#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильный тест Keys.so API с актуальными endpoints
Основано на реальной документации API
"""

import asyncio
import aiohttp
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Настройка кодировки
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


async def test_api_endpoints():
    """Тест всех endpoint'ов для ссылок"""

    api_key = os.getenv('KEYS_SO_API_KEY')
    headers = {
        'X-Keyso-TOKEN': api_key,
        'Content-Type': 'application/json'
    }

    test_domain = "vk.com"
    results = []

    print("=" * 80)
    print("ТЕСТИРОВАНИЕ KEYS.SO API - ПРАВИЛЬНЫЕ ENDPOINTS")
    print("=" * 80)
    print(f"Домен для тестирования: {test_domain}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as session:

        # 1. Domain Dashboard (GET)
        print("\n1. Domain Dashboard")
        url = "https://api.keys.so/report/simple/domain_dashboard"
        params = {"base": "msk", "domain": test_domain}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   DR: {data.get('dr', 'N/A')}")
                    print(f"   Traffic: {data.get('traffic', 'N/A')}")
                    results.append({"endpoint": "domain_dashboard", "success": True})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "domain_dashboard", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "domain_dashboard", "success": False})

        await asyncio.sleep(1)

        # 2. Backlinks (Входящие ссылки) - GET
        print("\n2. Backlinks (Входящие ссылки)")
        url = "https://api.keys.so/report/simple/links/backlinks"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total backlinks: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First backlink from: {first_item.get('source_name', 'N/A')}")
                        print(f"   Source DR: {first_item.get('source_dr', 'N/A')}")
                    results.append({"endpoint": "backlinks", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "backlinks", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "backlinks", "success": False})

        await asyncio.sleep(1)

        # 3. Backlinks Domains (Ссылающиеся домены) - GET
        print("\n3. Backlinks Domains (Ссылающиеся домены)")
        url = "https://api.keys.so/report/simple/links/backlinks-domains"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total referring domains: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First domain: {first_item.get('name', 'N/A')}")
                        print(f"   Outlinks count: {first_item.get('outlinks_count', 'N/A')}")
                    results.append({"endpoint": "backlinks-domains", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "backlinks-domains", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "backlinks-domains", "success": False})

        await asyncio.sleep(1)

        # 4. Outlinks (Исходящие ссылки) - GET
        print("\n4. Outlinks (Исходящие ссылки)")
        url = "https://api.keys.so/report/simple/links/outlinks"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total outlinks: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First outlink to: {first_item.get('target_name', 'N/A')}")
                    results.append({"endpoint": "outlinks", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "outlinks", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "outlinks", "success": False})

        await asyncio.sleep(1)

        # 5. Outlinks Domains (Исходящие домены) - GET
        print("\n5. Outlinks Domains (Исходящие домены)")
        url = "https://api.keys.so/report/simple/links/outlinks-domains"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total outlink domains: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First domain: {first_item.get('name', 'N/A')}")
                    results.append({"endpoint": "outlinks-domains", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "outlinks-domains", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "outlinks-domains", "success": False})

        await asyncio.sleep(1)

        # 6. Backlinks by IP - GET
        print("\n6. Backlinks by IP")
        url = "https://api.keys.so/report/simple/links/backlinks-ip"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total IPs: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    results.append({"endpoint": "backlinks-ip", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "backlinks-ip", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "backlinks-ip", "success": False})

        await asyncio.sleep(1)

        # 7. Backlinks by IP Subnets - GET
        print("\n7. Backlinks by IP Subnets")
        url = "https://api.keys.so/report/simple/links/backlinks-ip/subnet"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total subnets: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    results.append({"endpoint": "backlinks-ip-subnet", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "backlinks-ip-subnet", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "backlinks-ip-subnet", "success": False})

        await asyncio.sleep(1)

        # 8. Backlinks Anchors - GET
        print("\n8. Backlinks Anchors (Анкоры)")
        url = "https://api.keys.so/report/simple/links/backlinks-anchor"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total anchors: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First anchor: {first_item.get('anchor', 'N/A')[:50]}...")
                    results.append({"endpoint": "backlinks-anchor", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "backlinks-anchor", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "backlinks-anchor", "success": False})

        await asyncio.sleep(1)

        # 9. Popular Pages - GET
        print("\n9. Popular Pages (Популярные страницы)")
        url = "https://api.keys.so/report/simple/links/pages"
        params = {"domain": test_domain, "page": 1, "per_page": 10}

        try:
            async with session.get(url, params=params) as response:
                status = response.status
                print(f"   Status: {status}")
                if status == 200:
                    data = await response.json()
                    print(f"   SUCCESS")
                    print(f"   Total pages: {data.get('total', 0)}")
                    print(f"   Items on page: {len(data.get('data', []))}")
                    if data.get('data'):
                        first_item = data['data'][0]
                        print(f"   First page: {first_item.get('url', 'N/A')[:60]}...")
                    results.append({"endpoint": "pages", "success": True, "count": data.get('total', 0)})
                else:
                    text = await response.text()
                    print(f"   FAILED: {text[:150]}")
                    results.append({"endpoint": "pages", "success": False})
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({"endpoint": "pages", "success": False})

    # Итоговый отчет
    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\nВсего тестов: {len(results)}")
    print(f"Успешных: {successful}")
    print(f"Неудачных: {failed}")
    print(f"Процент успеха: {(successful/len(results)*100):.1f}%")

    if successful > 0:
        print("\nУспешные endpoints:")
        for r in results:
            if r["success"]:
                count_str = f" ({r['count']} items)" if 'count' in r else ""
                print(f"  + {r['endpoint']}{count_str}")

    if failed > 0:
        print("\nНеудачные endpoints:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['endpoint']}")

    # Сохранение результатов
    filename = f"keys_api_correct_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "test_domain": test_domain,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed
            }
        }, f, indent=2, ensure_ascii=False)

    print(f"\nРезультаты сохранены в: {filename}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
