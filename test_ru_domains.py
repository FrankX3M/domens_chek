#!/usr/bin/env python3
import asyncio
from src.availability import DomainAvailabilityChecker

async def test():
    checker = DomainAvailabilityChecker()

    test_domains = ['ya.ru', 'yandex.ru', 'google.com', 'defektoskopist.ru']
    results = await checker.check_domains(test_domains)

    print(f"Результаты проверки {len(results)} доменов:\n")
    for r in results:
        print(f"{r.domain:30} -> {r.status.value:12} via {r.checked_via}")

if __name__ == "__main__":
    asyncio.run(test())
