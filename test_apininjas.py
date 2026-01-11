#!/usr/bin/env python3
"""
Тест API Ninjas WHOIS API
10,000 бесплатных запросов/месяц
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()


async def test_apininjas():
    """Тестируем API Ninjas"""

    api_key = os.getenv('WHOIS_API_KEY')

    print("="*70)
    print("API Ninjas WHOIS API Test")
    print("="*70)
    print("Website: https://api-ninjas.com")
    print("Free tier: 10,000 requests/month")
    print("="*70)

    if not api_key or api_key == 'your_whois_api_key':
        print("\n[ERROR] WHOIS_API_KEY not configured!")
        print("\nQuick Setup:")
        print("1. Register at https://api-ninjas.com")
        print("2. Copy your API key from dashboard")
        print("3. Add to .env file:")
        print("   WHOIS_API_KEY=your_api_ninjas_key")
        print("   WHOIS_API_PROVIDER=apininjas")
        print("\nSee SETUP_API_NINJAS.md for detailed instructions")
        return

    print(f"\nAPI Key: {api_key[:20]}..." if len(api_key) > 20 else f"API Key: {api_key}")

    # Тестовые домены
    test_domains = [
        ("google.com", "Should be REGISTERED"),
        ("yandex.ru", "Should be REGISTERED"),
        ("mail.ru", "Should be REGISTERED"),
        ("thisisverylongunusualdomainname12345xyz.com", "Likely AVAILABLE")
    ]

    successful = 0
    failed = 0

    for domain, expected in test_domains:
        print(f"\n{'='*70}")
        print(f"Testing: {domain}")
        print(f"Expected: {expected}")
        print(f"{'='*70}")

        url = "https://api.api-ninjas.com/v1/whois"
        params = {"domain": domain}
        headers = {"X-Api-Key": api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    print(f"HTTP Status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print("\nJSON Response (key fields):")

                        # Основные поля
                        key_fields = ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'name_servers']
                        for field in key_fields:
                            value = data.get(field)
                            if value:
                                # Ограничиваем длину вывода
                                value_str = str(value)
                                if len(value_str) > 100:
                                    value_str = value_str[:100] + "..."
                                print(f"  - {field}: {value_str}")

                        # Определяем статус
                        if not data or not data.get('domain_name'):
                            print("\n=> Domain is AVAILABLE")
                            successful += 1
                        else:
                            print("\n=> Domain is REGISTERED")
                            print(f"   Registrar: {data.get('registrar', 'Unknown')}")
                            successful += 1

                    elif response.status == 400:
                        print("=> Bad Request (invalid domain or API error)")
                        text = await response.text()
                        print(f"   Error: {text[:200]}")
                        failed += 1
                    elif response.status == 401:
                        print("=> Unauthorized (invalid API key)")
                        print("   Check your API key in .env file")
                        failed += 1
                    elif response.status == 429:
                        print("=> Rate Limit Exceeded")
                        print("   You've used all 10,000 requests for this month")
                        failed += 1
                    else:
                        text = await response.text()
                        print(f"=> Unexpected status code")
                        print(f"   Error: {text[:200]}")
                        failed += 1

        except asyncio.TimeoutError:
            print("=> Timeout error")
            failed += 1
        except Exception as e:
            print(f"=> Exception: {e}")
            failed += 1

        await asyncio.sleep(1)  # Пауза между запросами

    # Итоги
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(test_domains)}")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {failed}")

    if successful == len(test_domains):
        print("\n[OK] All tests passed!")
        print("Your API Ninjas configuration is working correctly.")
        print("\nYou can now use the domain analyzer:")
        print("  python domain_analyzer.py yandex.ru --limit 100")
    elif successful > 0:
        print("\n[WARNING] Some tests failed")
        print("Check the errors above for details")
    else:
        print("\n[ERROR] All tests failed")
        print("Please check:")
        print("  1. Your API key is correct")
        print("  2. You have remaining requests (10,000/month)")
        print("  3. Your internet connection is working")

    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_apininjas())
