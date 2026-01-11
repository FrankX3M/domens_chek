#!/usr/bin/env python3
"""
Полная проверка всех endpoint'ов Keys.so API
Основано на документации: https://apidoc.keys.so/#tag/Ssylki
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()


class KeysAPITester:
    """Класс для тестирования всех endpoint'ов Keys.so API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.keys.so"
        self.headers = {
            'X-Keyso-TOKEN': api_key,
            'Content-Type': 'application/json'
        }
        self.results = []

    async def test_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        params: Dict[str, Any],
        method: str = "GET",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Тестирование одного endpoint'а

        Args:
            session: HTTP сессия
            endpoint: Путь к endpoint
            params: Параметры запроса
            method: HTTP метод (GET/POST)
            description: Описание endpoint'а

        Returns:
            Результаты теста
        """
        url = f"{self.base_url}{endpoint}"
        result = {
            "endpoint": endpoint,
            "description": description,
            "method": method,
            "params": params,
            "status": None,
            "success": False,
            "error": None,
            "data_preview": None,
            "timestamp": datetime.now().isoformat()
        }

        try:
            if method.upper() == "GET":
                async with session.get(url, params=params) as response:
                    result["status"] = response.status

                    if response.status == 200:
                        data = await response.json()
                        result["success"] = True
                        result["data_preview"] = self._preview_data(data)
                    else:
                        result["error"] = await response.text()

            elif method.upper() == "POST":
                async with session.post(url, json=params) as response:
                    result["status"] = response.status

                    if response.status == 200:
                        data = await response.json()
                        result["success"] = True
                        result["data_preview"] = self._preview_data(data)
                    else:
                        result["error"] = await response.text()

        except Exception as e:
            result["error"] = str(e)

        return result

    def _preview_data(self, data: Any) -> Dict[str, Any]:
        """Создание превью данных для отчета"""
        preview = {}

        if isinstance(data, dict):
            preview["keys"] = list(data.keys())

            if "data" in data:
                data_items = data["data"]
                if isinstance(data_items, list):
                    preview["data_count"] = len(data_items)
                    if data_items:
                        preview["first_item_keys"] = list(data_items[0].keys()) if isinstance(data_items[0], dict) else None

            if "total" in data:
                preview["total"] = data["total"]

            if "current_page" in data:
                preview["current_page"] = data["current_page"]

        return preview

    async def run_all_tests(self, test_domain: str = "vk.com"):
        """
        Запуск всех тестов

        Args:
            test_domain: Домен для тестирования
        """
        print(f"\n{'='*80}")
        print(f"ТЕСТИРОВАНИЕ KEYS.SO API")
        print(f"Домен для тестирования: {test_domain}")
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:

            # 1. Входящие ссылки (Incoming Links)
            print("📥 Тестирование: Входящие ссылки...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/incoming",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Получение входящих ссылок на домен"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 2. Исходящие ссылки (Outgoing Links)
            print("\n📤 Тестирование: Исходящие ссылки...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/outgoing",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Получение исходящих ссылок с домена"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 3. Ссылающиеся домены (Referring Domains)
            print("\n🔗 Тестирование: Ссылающиеся домены...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/referring_domains",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Получение доменов, ссылающихся на целевой домен"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 4. Ссылающиеся домены с данными
            print("\n🔗📊 Тестирование: Ссылающиеся домены с метриками...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/referring_domains_with_data",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Ссылающиеся домены с детальными метриками"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 5. Исходящие домены
            print("\n➡️ Тестирование: Исходящие домены...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/outgoing_domains",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Домены, на которые ссылается целевой домен"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 6. Исходящие домены с данными
            print("\n➡️📊 Тестирование: Исходящие домены с метриками...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/outgoing_domains_with_data",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Исходящие домены с детальными метриками"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 7. Ссылки по IP
            print("\n🌐 Тестирование: Ссылки по IP адресам...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/by_ip",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Группировка ссылающихся доменов по IP"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 8. Ссылки по подсетям IP
            print("\n🌐📶 Тестирование: Ссылки по IP подсетям...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/by_ip_subnets",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Группировка ссылающихся доменов по IP подсетям"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 9. Анкоры (Anchors)
            print("\n⚓ Тестирование: Анкоры ссылок...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/anchors",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Анализ анкорных текстов ссылок"
            )
            self.results.append(result)
            self._print_result(result)
            await asyncio.sleep(1)

            # 10. Популярные страницы
            print("\n⭐ Тестирование: Популярные страницы...")
            result = await self.test_endpoint(
                session,
                "/report/simple/links/popular_pages",
                {"domain": test_domain, "base": "msk", "per_page": 10, "page": 1},
                method="POST",
                description="Наиболее популярные страницы домена по ссылкам"
            )
            self.results.append(result)
            self._print_result(result)

        # Печать итогового отчета
        self._print_summary()

        # Сохранение результатов в файл
        self._save_results()

    def _print_result(self, result: Dict[str, Any]):
        """Печать результата теста"""
        if result["success"]:
            print(f"  ✅ Статус: {result['status']} - SUCCESS")
            if result["data_preview"]:
                preview = result["data_preview"]
                if "data_count" in preview:
                    print(f"  📊 Получено записей: {preview['data_count']}")
                if "total" in preview:
                    print(f"  📈 Всего доступно: {preview['total']}")
                if "first_item_keys" in preview and preview["first_item_keys"]:
                    print(f"  🔑 Поля данных: {', '.join(preview['first_item_keys'][:5])}...")
        else:
            print(f"  ❌ Статус: {result['status']} - FAILED")
            if result["error"]:
                error_preview = result["error"][:200]
                print(f"  ⚠️  Ошибка: {error_preview}")

    def _print_summary(self):
        """Печать итогового отчета"""
        print(f"\n{'='*80}")
        print("ИТОГОВЫЙ ОТЧЕТ")
        print(f"{'='*80}\n")

        successful = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - successful

        print(f"Всего тестов: {len(self.results)}")
        print(f"✅ Успешных: {successful}")
        print(f"❌ Неудачных: {failed}")
        print(f"📊 Процент успеха: {(successful/len(self.results)*100):.1f}%\n")

        if failed > 0:
            print("Неудачные endpoint'ы:")
            for result in self.results:
                if not result["success"]:
                    print(f"  ❌ {result['endpoint']} (Статус: {result['status']})")

        print(f"\n{'='*80}\n")

    def _save_results(self):
        """Сохранение результатов в JSON файл"""
        filename = f"keys_api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "api_url": self.base_url,
                "total_tests": len(self.results),
                "successful": sum(1 for r in self.results if r["success"]),
                "failed": sum(1 for r in self.results if not r["success"]),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"📁 Результаты сохранены в: {filename}")


async def main():
    """Главная функция"""
    # Настройка кодировки для Windows
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    api_key = os.getenv('KEYS_SO_API_KEY')

    if not api_key:
        print("❌ Ошибка: KEYS_SO_API_KEY не найден в .env файле")
        return

    print(f"🔑 API Key загружен: {api_key[:20]}...")

    # Создаем тестер
    tester = KeysAPITester(api_key)

    # Запускаем все тесты
    await tester.run_all_tests(test_domain="vk.com")


if __name__ == "__main__":
    asyncio.run(main())
