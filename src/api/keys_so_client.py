"""
Keys.so API Client
Клиент для работы с API Keys.so
"""

import logging
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KeysSoClient:
    """Клиент для работы с Keys.so API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.keys.so",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Инициализация клиента

        Args:
            api_key: API ключ Keys.so
            base_url: Базовый URL API
            timeout: Таймаут запросов в секундах
            max_retries: Максимальное количество повторных попыток
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("Keys.so API клиент инициализирован")

    async def __aenter__(self):
        """Вход в контекстный менеджер"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'X-Keyso-TOKEN': self.api_key,
                'Content-Type': 'application/json'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        if self.session:
            await self.session.close()

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса к API

        Args:
            endpoint: Эндпоинт API
            params: Параметры запроса
            method: HTTP метод (GET или POST)

        Returns:
            Ответ API в виде словаря
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    request_method = self.session.get
                    kwargs = {"params": params}
                else:
                    request_method = self.session.post
                    kwargs = {"json": params}

                async with request_method(url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise Exception("Ошибка авторизации. Проверьте API ключ")
                    elif response.status == 429:
                        logger.warning("Rate limit exceeded. Waiting before retry...")
                        if attempt < self.max_retries - 1:
                            import asyncio
                            await asyncio.sleep(10)
                            continue
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Failed to make request after {self.max_retries} attempts: {e}")

        raise Exception("Max retries exceeded")

    async def get_referring_domains(
        self,
        domain: str,
        per_page: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Получение ссылающихся доменов (backlinks-domains)

        Args:
            domain: Домен для анализа
            per_page: Количество записей на страницу (по умолчанию 100)
            page: Номер страницы

        Returns:
            Словарь с данными о ссылающихся доменах
        """
        endpoint = "/report/simple/links/backlinks-domains"
        params = {
            'domain': domain,
            'per_page': per_page,
            'page': page
        }

        logger.debug(f"Запрос ссылающихся доменов для {domain} (страница {page})")
        return await self._make_request(endpoint, params, method="GET")

    async def get_backlinks(
        self,
        domain: str,
        limit: int = 100000
    ) -> List[Dict[str, Any]]:
        """
        Получение обратных ссылок для домена (входящие ссылки)

        Args:
            domain: Домен для анализа
            limit: Максимальное количество ссылок

        Returns:
            Список обратных ссылок
        """
        logger.info(f"Получение входящих ссылок для {domain}")

        all_results = []
        per_page = 100  # Безопасное значение для API
        page = 1

        try:
            while len(all_results) < limit:
                endpoint = "/report/simple/links/backlinks"
                params = {
                    'domain': domain,
                    'per_page': per_page,
                    'page': page
                }

                response = await self._make_request(endpoint, params, method="GET")

                # Проверяем структуру ответа
                if not response or 'data' not in response:
                    logger.warning(f"Unexpected response structure: {response}")
                    break

                data = response['data']
                if not data:
                    logger.info("Больше нет данных")
                    break

                all_results.extend(data)

                # Проверяем, есть ли еще страницы
                total = response.get('total', 0)
                current_page = response.get('current_page', page)
                last_page = response.get('last_page', 0)

                logger.info(f"Получено {len(all_results)} из {total} ссылок (страница {current_page}/{last_page})")

                if len(all_results) >= limit or current_page >= last_page or len(data) < per_page:
                    break

                page += 1

                # Защита от rate limit
                import asyncio
                await asyncio.sleep(1)

            logger.info(f"Всего получено входящих ссылок: {len(all_results)}")
            return all_results

        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")
            raise

    async def get_all_outlinks(
        self,
        domain: str,
        limit: int = 100000
    ) -> List[Dict[str, Any]]:
        """
        Получение всех исходящих ссылок для домена

        Args:
            domain: Домен для анализа
            limit: Максимальное количество ссылок

        Returns:
            Список исходящих ссылок
        """
        logger.info(f"Получение исходящих ссылок для {domain}")

        all_results = []
        per_page = 100
        page = 1

        try:
            while len(all_results) < limit:
                endpoint = "/report/simple/links/outlinks"
                params = {
                    'domain': domain,
                    'per_page': per_page,
                    'page': page
                }

                response = await self._make_request(endpoint, params, method="GET")

                # Проверяем структуру ответа
                if not response or 'data' not in response:
                    logger.warning(f"Unexpected response structure: {response}")
                    break

                data = response['data']
                if not data:
                    logger.info("Больше нет данных")
                    break

                all_results.extend(data)

                # Проверяем, есть ли еще страницы
                total = response.get('total', 0)
                current_page = response.get('current_page', page)
                last_page = response.get('last_page', 0)

                logger.info(f"Получено {len(all_results)} из {total} ссылок (страница {current_page}/{last_page})")

                if len(all_results) >= limit or current_page >= last_page or len(data) < per_page:
                    break

                page += 1

                # Защита от rate limit
                import asyncio
                await asyncio.sleep(1)

            logger.info(f"Всего получено исходящих ссылок: {len(all_results)}")
            return all_results

        except Exception as e:
            logger.error(f"Ошибка при получении исходящих ссылок: {e}")
            raise

    async def get_domain_metrics(
        self,
        domain: str,
        base: str = "msk"
    ) -> Optional[Dict[str, Any]]:
        """
        Получение метрик домена (DR, трафик и т.д.)

        Args:
            domain: Домен для получения метрик
            base: База данных (по умолчанию msk)

        Returns:
            Словарь с метриками или None
        """
        logger.debug(f"Получение метрик для {domain}")

        try:
            endpoint = "/report/simple/domain_dashboard"
            params = {
                'base': base,
                'domain': domain
            }

            response = await self._make_request(endpoint, params, method="GET")
            return response

        except Exception as e:
            logger.warning(f"Не удалось получить метрики для {domain}: {e}")
            return None

    async def get_backlinks_domains(
        self,
        domain: str,
        per_page: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Получение списка доменов, ссылающихся на целевой домен

        Args:
            domain: Домен для анализа
            per_page: Количество записей на страницу
            page: Номер страницы

        Returns:
            Словарь с данными о ссылающихся доменах
        """
        endpoint = "/report/simple/links/backlinks-domains"
        params = {
            'domain': domain,
            'per_page': per_page,
            'page': page
        }

        logger.debug(f"Запрос доменов, ссылающихся на {domain} (страница {page})")
        return await self._make_request(endpoint, params, method="GET")

    async def get_outlinks(
        self,
        domain: str,
        per_page: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Получение исходящих ссылок домена

        Args:
            domain: Домен для анализа
            per_page: Количество записей на страницу
            page: Номер страницы

        Returns:
            Словарь с данными об исходящих ссылках
        """
        endpoint = "/report/simple/links/outlinks"
        params = {
            'domain': domain,
            'per_page': per_page,
            'page': page
        }

        logger.debug(f"Запрос исходящих ссылок для {domain} (страница {page})")
        return await self._make_request(endpoint, params, method="GET")

    async def get_outlinks_domains(
        self,
        domain: str,
        per_page: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Получение списка доменов, на которые ссылается целевой домен

        Args:
            domain: Домен для анализа
            per_page: Количество записей на страницу
            page: Номер страницы

        Returns:
            Словарь с данными об исходящих доменах
        """
        endpoint = "/report/simple/links/outlinks-domains"
        params = {
            'domain': domain,
            'per_page': per_page,
            'page': page
        }

        logger.debug(f"Запрос исходящих доменов для {domain} (страница {page})")
        return await self._make_request(endpoint, params, method="GET")
