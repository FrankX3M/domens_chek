#!/usr/bin/env python3
import asyncio
import json
from src.api.keys_so_client import KeysSoClient
from src.utils.config import APIConfig

async def test():
    config = APIConfig.from_env()
    async with KeysSoClient(config.api_key) as client:
        # Тест входящей ссылки (backlink)
        backlink_result = await client.get_backlinks('yandex.ru', limit=1)
        print("=== Структура BACKLINK (входящая ссылка) ===")
        if backlink_result:
            print(json.dumps(backlink_result[0], indent=2, ensure_ascii=False))

        print("\n" + "="*60 + "\n")

        # Тест исходящей ссылки (outlink)
        outlink_result = await client.get_outlinks('yandex.ru', per_page=1, page=1)
        print("=== Структура OUTLINK (исходящая ссылка) ===")
        if outlink_result and outlink_result.get('data'):
            print(json.dumps(outlink_result['data'][0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test())
