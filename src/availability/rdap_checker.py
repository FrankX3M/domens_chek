import aiohttp
import asyncio
from typing import Optional
import logging
import tldextract
from datetime import datetime

from ..models.domain_status import DomainCheckResult, DomainStatus, CheckMethod
from .bootstrap_loader import RDAPBootstrapLoader

logger = logging.getLogger(__name__)


class RDAPChecker:
    """Проверка доступности доменов через RDAP"""
    
    def __init__(
        self,
        bootstrap_loader: RDAPBootstrapLoader,
        timeout: int = 5,
        max_retries: int = 2
    ):
        self.bootstrap = bootstrap_loader
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.tld_extract = tldextract.TLDExtract(cache_dir='.tld_cache')
    
    async def check_domain(self, domain: str) -> Optional[DomainCheckResult]:
        """
        Проверка домена через RDAP
        
        Args:
            domain: Доменное имя для проверки
        
        Returns:
            DomainCheckResult если проверка успешна, None если RDAP не поддерживается
        """
        # Извлекаем TLD
        extracted = self.tld_extract(domain)
        tld = extracted.suffix
        
        if not tld:
            logger.warning(f"Не удалось извлечь TLD из {domain}")
            return None
        
        # Проверяем поддержку RDAP
        rdap_servers = self.bootstrap.get_rdap_servers(tld)
        if not rdap_servers:
            logger.debug(f"TLD '{tld}' не поддерживает RDAP")
            return None
        
        # Нормализуем домен
        normalized_domain = f"{extracted.domain}.{tld}".lower()
        
        # Пробуем проверить через каждый сервер
        for server_url in rdap_servers:
            result = await self._query_rdap_server(
                server_url, normalized_domain, tld
            )
            if result:
                return result
        
        # Все серверы не ответили
        logger.warning(
            f"Все RDAP серверы для {domain} ({tld}) не ответили"
        )
        return None
    
    async def _query_rdap_server(
        self,
        server_url: str,
        domain: str,
        tld: str
    ) -> Optional[DomainCheckResult]:
        """
        Запрос к конкретному RDAP серверу
        
        Args:
            server_url: URL RDAP сервера
            domain: Нормализованный домен
            tld: Top-level domain
        
        Returns:
            DomainCheckResult или None при ошибке
        """
        # Формируем URL запроса
        query_url = f"{server_url.rstrip('/')}/domain/{domain}"
        
        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(query_url) as response:
                        if response.status == 200:
                            # Домен зарегистрирован
                            data = await response.json()
                            return DomainCheckResult(
                                domain=domain,
                                status=DomainStatus.REGISTERED,
                                check_method=CheckMethod.RDAP,
                                checked_at=datetime.now(),
                                tld_supports_rdap=True
                            )
                        
                        elif response.status == 404:
                            # Домен свободен
                            return DomainCheckResult(
                                domain=domain,
                                status=DomainStatus.AVAILABLE,
                                check_method=CheckMethod.RDAP,
                                checked_at=datetime.now(),
                                tld_supports_rdap=True
                            )
                        
                        elif response.status >= 500:
                            # Ошибка сервера - retry
                            if attempt < self.max_retries:
                                logger.debug(
                                    f"RDAP server error {response.status} "
                                    f"for {domain}, retry {attempt}/{self.max_retries}"
                                )
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                logger.warning(
                                    f"RDAP server persistent error for {domain}"
                                )
                                return None
                        
                        else:
                            # Другая ошибка
                            logger.warning(
                                f"Unexpected RDAP response {response.status} "
                                f"for {domain}"
                            )
                            return None
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    logger.debug(
                        f"RDAP timeout for {domain}, "
                        f"retry {attempt}/{self.max_retries}"
                    )
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.warning(f"RDAP timeout for {domain} after {self.max_retries} attempts")
                    return None
            
            except Exception as e:
                logger.debug(f"RDAP error for {domain}: {e}")
                return None
        
        return None
