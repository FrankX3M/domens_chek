import aiohttp
import asyncio
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..models.domain_status import DomainCheckResult, DomainStatus, CheckMethod

logger = logging.getLogger(__name__)


class WHOISChecker:
    """Проверка доступности доменов через WHOIS API"""
    
    def __init__(
        self,
        api_provider: str = "whoisxml",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        self.api_provider = api_provider.lower()
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        
        # Настройка URL в зависимости от провайдера
        if self.api_provider == "whoisxml":
            self.base_url = base_url or "https://domain-availability.whoisxmlapi.com/api/v1"
        elif self.api_provider == "apininjas":
            self.base_url = base_url or "https://api.api-ninjas.com/v1"
        elif self.api_provider == "whoapi":
            self.base_url = base_url or "https://api.whoapi.com"
        elif self.api_provider == "whoxy":
            self.base_url = base_url or "https://api.whoxy.com"
        elif self.api_provider == "jsonwhois":
            self.base_url = base_url or "https://jsonwhoisapi.com/api/v1"
        elif self.api_provider == "whodat":
            self.base_url = base_url or "https://who-dat.as93.net"
        else:
            self.base_url = base_url or ""
    
    async def check_domain(self, domain: str) -> DomainCheckResult:
        """
        Проверка домена через WHOIS API
        
        Args:
            domain: Доменное имя
        
        Returns:
            DomainCheckResult с результатом проверки
        """
        logger.debug(f"Проверка {domain} через WHOIS API ({self.api_provider})")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.api_provider == "whoisxml":
                    result = await self._check_whoisxml(domain)
                elif self.api_provider == "apininjas":
                    result = await self._check_apininjas(domain)
                elif self.api_provider == "whoapi":
                    result = await self._check_whoapi(domain)
                elif self.api_provider == "whoxy":
                    result = await self._check_whoxy(domain)
                elif self.api_provider == "jsonwhois":
                    result = await self._check_jsonwhois(domain)
                elif self.api_provider == "whodat":
                    result = await self._check_whodat(domain)
                elif self.api_provider == "local":
                    result = await self._check_local_whois(domain)
                else:
                    raise ValueError(f"Неизвестный WHOIS провайдер: {self.api_provider}")
                
                if result:
                    return result
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    delay = 2 ** attempt
                    logger.debug(
                        f"WHOIS timeout for {domain}, "
                        f"retry {attempt}/{self.max_retries} after {delay}s"
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"WHOIS timeout for {domain} after {self.max_retries} attempts")
            
            except Exception as e:
                logger.error(f"WHOIS error for {domain}: {e}")
        
        # Все попытки исчерпаны
        return DomainCheckResult(
            domain=domain,
            status=DomainStatus.UNKNOWN,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now(),
            error_message=f"Failed after {self.max_retries} attempts"
        )
    
    async def _check_whoisxml(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через WhoisXML API"""
        if not self.api_key:
            raise ValueError("WhoisXML API key не указан")
        
        url = f"{self.base_url}/domainAvailability"
        params = {
            "apiKey": self.api_key,
            "domainName": domain
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(
                        f"WhoisXML API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None
                
                data = await response.json()
        
        # Парсинг ответа
        domain_availability = data.get('DomainInfo', {}).get('domainAvailability')
        
        if domain_availability == 'AVAILABLE':
            status = DomainStatus.AVAILABLE
        elif domain_availability == 'UNAVAILABLE':
            status = DomainStatus.REGISTERED
        else:
            status = DomainStatus.UNKNOWN
        
        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now()
        )
    
    async def _check_apininjas(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через API Ninjas"""
        if not self.api_key:
            raise ValueError("API Ninjas key не указан")
        
        url = f"{self.base_url}/whois"
        params = {"domain": domain}
        headers = {"X-Api-Key": self.api_key}
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        f"API Ninjas error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None
                
                data = await response.json()
        
        # Определяем статус по наличию данных
        # API Ninjas возвращает пустой объект для незарегистрированных доменов
        if not data or not data.get('domain_name'):
            status = DomainStatus.AVAILABLE
        else:
            status = DomainStatus.REGISTERED
        
        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now(),
            registrar=data.get('registrar')
        )
    
    async def _check_whoapi(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через WhoAPI (10,000 бесплатных запросов)"""
        if not self.api_key:
            raise ValueError("WhoAPI key не указан")

        url = f"{self.base_url}/"
        params = {
            "apikey": self.api_key,
            "domain": domain,
            "r": "taken"  # проверка доступности
        }

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(
                        f"WhoAPI error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None

                data = await response.json()

        # WhoAPI возвращает:
        # status: 0 (success), taken: 0/1 (0=доступен, 1=занят)
        if data.get('status') == 0:
            taken = data.get('taken', 1)
            status = DomainStatus.REGISTERED if taken == 1 else DomainStatus.AVAILABLE
        else:
            status = DomainStatus.UNKNOWN

        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now()
        )

    async def _check_whoxy(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через Whoxy (до 250k бесплатных запросов после одобрения)"""
        if not self.api_key:
            raise ValueError("Whoxy API key не указан")

        url = f"{self.base_url}/"
        params = {
            "key": self.api_key,
            "whois": domain
        }

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(
                        f"Whoxy API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None

                data = await response.json()

        # Whoxy возвращает полную WHOIS информацию
        # Если домен свободен, данные будут минимальны или статус будет указывать на это
        if data.get('status') == 1:  # success
            # Если есть registrar_name или domain_registered, домен занят
            if data.get('domain_registered') or data.get('registrar_name'):
                status = DomainStatus.REGISTERED
            else:
                status = DomainStatus.AVAILABLE
        else:
            status = DomainStatus.UNKNOWN

        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now(),
            registrar=data.get('registrar_name')
        )

    async def _check_jsonwhois(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через JsonWhois (pay-as-you-go с бесплатными запросами)"""
        if not self.api_key:
            raise ValueError("JsonWhois API key не указан")

        url = f"{self.base_url}/whois"
        params = {
            "identifier": domain
        }
        headers = {
            "Authorization": f"Token token={self.api_key}"
        }

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        f"JsonWhois API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None

                data = await response.json()

        # JsonWhois возвращает полные WHOIS данные
        # Если домен свободен, обычно поле registered будет false или данные минимальны
        if data.get('registered') is False:
            status = DomainStatus.AVAILABLE
        elif data.get('registered') is True or data.get('domain_name'):
            status = DomainStatus.REGISTERED
        else:
            status = DomainStatus.UNKNOWN

        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now(),
            registrar=data.get('registrar')
        )

    async def _check_whodat(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через Who-Dat (бесплатный open-source сервис)"""
        # Who-Dat не требует API ключ
        url = f"{self.base_url}/{domain}"

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url) as response:
                if response.status == 404:
                    # 404 обычно означает что домен не найден (свободен)
                    return DomainCheckResult(
                        domain=domain,
                        status=DomainStatus.AVAILABLE,
                        check_method=CheckMethod.WHOIS_API,
                        checked_at=datetime.now()
                    )
                elif response.status != 200:
                    logger.error(
                        f"Who-Dat API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None

                data = await response.json()

        # Who-Dat возвращает WHOIS данные если домен зарегистрирован
        if data and (data.get('domain') or data.get('domainName')):
            status = DomainStatus.REGISTERED
        else:
            status = DomainStatus.AVAILABLE

        return DomainCheckResult(
            domain=domain,
            status=status,
            check_method=CheckMethod.WHOIS_API,
            checked_at=datetime.now(),
            registrar=data.get('registrar')
        )

    async def _check_local_whois(self, domain: str) -> Optional[DomainCheckResult]:
        """Проверка через локальный python-whois (fallback)"""
        try:
            import whois

            # python-whois - синхронная библиотека, запускаем в executor
            loop = asyncio.get_event_loop()
            domain_info = await loop.run_in_executor(None, whois.whois, domain)

            # Если domain_info пустой или domain_name None - домен свободен
            if not domain_info or not domain_info.domain_name:
                status = DomainStatus.AVAILABLE
            else:
                status = DomainStatus.REGISTERED

            return DomainCheckResult(
                domain=domain,
                status=status,
                check_method=CheckMethod.WHOIS_LOCAL,
                checked_at=datetime.now()
            )

        except ImportError:
            logger.error("python-whois не установлен")
            return None
        except Exception as e:
            logger.debug(f"Local WHOIS error for {domain}: {e}")
            return None
