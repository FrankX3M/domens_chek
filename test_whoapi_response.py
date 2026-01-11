#!/usr/bin/env python3
"""
Тест ответа WhoAPI
Показывает реальный ответ от WhoAPI для понимания формата
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()


async def test_whoapi_response():
    """Тестируем ответ WhoAPI"""

    api_key = os.getenv('WHOIS_API_KEY')

    if not api_key or api_key == 'your_whois_api_key':
        print("[ERROR] WHOIS_API_KEY not configured in .env")
        print("\nTo use WhoAPI:")
        print("1. Register at https://whoapi.com")
        print("2. Get your API key from dashboard")
        print("3. Add to .env:")
        print("   WHOIS_API_KEY=your_whoapi_key")
        print("   WHOIS_API_PROVIDER=whoapi")
        return

    print("="*70)
    print("WhoAPI Response Test")
    print("="*70)
    print(f"API Key: {api_key[:15]}...")

    # Тестовые домены
    test_domains = [
        ("google.com", "Should be REGISTERED (taken=1)"),
        ("yandex.ru", "Should be REGISTERED (taken=1)"),
        ("thisisverylongunusualdomainname12345.com", "Likely AVAILABLE (taken=0)")
    ]

    for domain, expected in test_domains:
        print(f"\n{'='*70}")
        print(f"Testing: {domain}")
        print(f"Expected: {expected}")
        print(f"{'='*70}")

        url = "https://api.whoapi.com/"
        params = {
            "apikey": api_key,
            "domain": domain,
            "r": "taken"  # Check availability
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
                        print(f"  - status: {data.get('status')} (0=success, 1+=error)")
                        print(f"  - taken: {data.get('taken')} (0=available, 1=registered)")

                        # Интерпретация
                        if data.get('status') == 0:
                            taken = data.get('taken', 1)
                            if taken == 0:
                                print(f"\n=> Domain is AVAILABLE")
                            elif taken == 1:
                                print(f"\n=> Domain is REGISTERED")
                        else:
                            print(f"\n=> API Error: {data.get('status_desc')}")
                    else:
                        text = await response.text()
                        print(f"Error response: {text}")

        except Exception as e:
            print(f"Exception: {e}")

        await asyncio.sleep(2)  # Пауза между запросами

    print("\n" + "="*70)
    print("\nIf you see errors, make sure:")
    print("1. You registered at https://whoapi.com")
    print("2. You copied the correct API key")
    print("3. Your .env has:")
    print("   WHOIS_API_KEY=your_actual_key")
    print("   WHOIS_API_PROVIDER=whoapi")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_whoapi_response())
