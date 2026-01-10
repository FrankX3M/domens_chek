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
