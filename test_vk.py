#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API с доменом vk.com
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем путь к src в sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.keys_so_client import KeysSoClient
from src.utils.logger import setup_logger
from src.utils.config import LogConfig

# Загружаем переменные окружения
load_dotenv()


async def test_vk():
    """Тестирование API с доменом vk.com"""

    # Настройка логирования
    log_config = LogConfig(level="DEBUG", file=None)
    logger = setup_logger(log_config)

    # Получаем API ключ
    api_key = os.getenv('KEYS_SO_API_KEY')
    if not api_key:
        logger.error("KEYS_SO_API_KEY не найден в .env")
        return

    logger.info("=" * 70)
    logger.info("Тест API Keys.so с доменом vk.com")
    logger.info("=" * 70)

    try:
        async with KeysSoClient(api_key=api_key) as client:
            # Получаем данные о ссылающихся доменах для vk.com
            logger.info("\nЗапрос данных для vk.com...")

            # Сначала получим первую страницу для проверки
            response = await client.get_referring_domains(
                domain="vk.com",
                per_page=10,
                page=1
            )

            logger.info(f"\nСтруктура ответа API:")
            logger.info(f"Ключи в ответе: {list(response.keys())}")

            if 'total' in response:
                logger.info(f"Всего ссылающихся доменов: {response['total']}")

            if 'data' in response and response['data']:
                logger.info(f"\nПолучено записей: {len(response['data'])}")
                logger.info(f"\nПример первой записи:")
                first_item = response['data'][0]
                for key, value in first_item.items():
                    logger.info(f"  {key}: {value}")

            logger.info("\n" + "=" * 70)
            logger.info("✓ Тест завершен успешно!")
            logger.info("=" * 70)

    except Exception as e:
        logger.exception(f"❌ Ошибка: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_vk())
    exit(exit_code if exit_code else 0)
