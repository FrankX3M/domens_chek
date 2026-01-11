#!/usr/bin/env python3
"""
Тест Who-Dat API (бесплатный, не требует API ключ)
"""

import asyncio
import aiohttp
import json


async def test_whodat():
    """Тестируем Who-Dat API"""

    print("="*70)
    print("Who-Dat API Test (FREE, no API key required)")
    print("="*70)
    print("URL: https://who-dat.as93.net")
    print("GitHub: https://github.com/Lissy93/who-dat")

    # Тестовые домены
    test_domains = [
        ("google.com", "Should be REGISTERED"),
        ("yandex.ru", "Should be REGISTERED"),
        ("thisisverylongunusualdomainname12345xyz.com", "Likely AVAILABLE")
    ]

    for domain, expected in test_domains:
        print(f"\n{'='*70}")
        print(f"Testing: {domain}")
        print(f"Expected: {expected}")
        print(f"{'='*70}")

        url = f"https://who-dat.as93.net/{domain}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    print(f"HTTP Status: {response.status}")

                    if response.status == 404:
                        print("\n=> Domain is AVAILABLE (404 = not found)")
                    elif response.status == 200:
                        data = await response.json()
                        print("\nJSON Response (first 500 chars):")
                        json_str = json.dumps(data, indent=2, ensure_ascii=False)
                        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

                        # Анализируем поля
                        print("\nKey fields:")
                        print(f"  - domain: {data.get('domain') or data.get('domainName')}")
                        print(f"  - registrar: {data.get('registrar')}")
                        print(f"  - status: {data.get('status')}")

                        if data.get('domain') or data.get('domainName'):
                            print("\n=> Domain is REGISTERED")
                        else:
                            print("\n=> Domain status UNKNOWN")
                    else:
                        text = await response.text()
                        print(f"Error response: {text[:200]}")

        except asyncio.TimeoutError:
            print(f"Timeout error - service may be slow or unavailable")
        except Exception as e:
            print(f"Exception: {e}")

        await asyncio.sleep(2)  # Пауза между запросами

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("Who-Dat is a free WHOIS/RDAP lookup service")
    print("Advantages:")
    print("  + No API key required")
    print("  + Free and open-source")
    print("  + No rate limits (fair use)")
    print("\nTo use in your project:")
    print("  WHOIS_API_PROVIDER=whodat")
    print("  # No API key needed!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_whodat())
