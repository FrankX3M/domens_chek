"""
Domain Availability Checker
Проверка доступности доменов через RDAP и WHOIS API
"""

import logging
import asyncio
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from .rdap_checker import RDAPChecker
from .bootstrap_loader import RDAPBootstrapLoader
from .whois_checker import WHOISChecker

logger = logging.getLogger(__name__)


class DomainStatus(Enum):
    """Статус домена"""
    REGISTERED = "REGISTERED"
    AVAILABLE = "AVAILABLE"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


@dataclass
class AvailabilityResult:
    """Результат проверки доступности домена"""
    domain: str
    status: DomainStatus
    checked_via: str  # "rdap", "whois", "error"
    error: Optional[str] = None


class DomainAvailabilityChecker:
    """Проверка доступности доменов"""

    def __init__(
        self,
        whois_api_key: Optional[str] = None,
        whois_provider: str = "whoisxml",
        max_concurrent: int = 20,
        skip_rdap: bool = False
    ):
        """
        Инициализация чекера

        Args:
            whois_api_key: API ключ для WHOIS сервиса
            whois_provider: Провайдер WHOIS API
            max_concurrent: Максимум параллельных запросов
            skip_rdap: Пропустить RDAP, использовать только WHOIS
        """
        self.whois_api_key = whois_api_key
        self.whois_provider = whois_provider
        self.max_concurrent = max_concurrent
        self.skip_rdap = skip_rdap

        # Инициализация компонентов
        self.bootstrap_loader = RDAPBootstrapLoader()
        self._bootstrap_loaded = False
        self.rdap_checker = RDAPChecker(self.bootstrap_loader) if not skip_rdap else None
        self.whois_checker = WHOISChecker(
            api_provider=whois_provider,
            api_key=whois_api_key
        ) if whois_api_key else None

        logger.info(
            f"Domain Availability Checker инициализирован "
            f"(max_concurrent={max_concurrent}, skip_rdap={skip_rdap})"
        )

    async def _ensure_bootstrap_loaded(self):
        """Гарантирует, что bootstrap данные загружены"""
        if not self._bootstrap_loaded and self.rdap_checker:
            await self.bootstrap_loader.load()
            self._bootstrap_loaded = True

    async def check_domain(self, domain: str) -> AvailabilityResult:
        """
        Проверка одного домена

        Args:
            domain: Домен для проверки

        Returns:
            Результат проверки
        """
        # Загружаем bootstrap если еще не загружен
        await self._ensure_bootstrap_loaded()

        # Пытаемся через RDAP (если не отключен)
        if self.rdap_checker:
            try:
                rdap_result = await self.rdap_checker.check_domain(domain)
                if rdap_result:
                    return AvailabilityResult(
                        domain=domain,
                        status=DomainStatus[rdap_result.status.value],
                        checked_via="rdap"
                    )
            except Exception as e:
                logger.debug(f"RDAP check failed for {domain}: {e}")

        # Fallback на WHOIS API (если есть ключ)
        if self.whois_checker:
            try:
                whois_result = await self.whois_checker.check_domain(domain)
                if whois_result:
                    return AvailabilityResult(
                        domain=domain,
                        status=DomainStatus[whois_result.status.value],
                        checked_via="whois"
                    )
            except Exception as e:
                logger.debug(f"WHOIS check failed for {domain}: {e}")

        # Если ничего не сработало - помечаем как REGISTERED (по умолчанию)
        # Это безопаснее чем пометить как AVAILABLE
        return AvailabilityResult(
            domain=domain,
            status=DomainStatus.REGISTERED,
            checked_via="default",
            error="Could not verify domain availability"
        )
    
    async def check_domains(
        self,
        domains: List[str]
    ) -> List[AvailabilityResult]:
        """
        Проверка списка доменов с параллельной обработкой

        Args:
            domains: Список доменов для проверки

        Returns:
            Список результатов проверки
        """
        logger.info(f"Проверка доступности {len(domains)} доменов")

        # Создаем семафор для ограничения параллельных запросов
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_with_semaphore(domain: str) -> AvailabilityResult:
            async with semaphore:
                return await self.check_domain(domain)

        # Запускаем проверки параллельно
        tasks = [check_with_semaphore(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обработка результатов и исключений
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error checking {domains[i]}: {result}")
                final_results.append(AvailabilityResult(
                    domain=domains[i],
                    status=DomainStatus.ERROR,
                    checked_via="error",
                    error=str(result)
                ))
            else:
                final_results.append(result)

        # Статистика
        available = sum(1 for r in final_results if r.status == DomainStatus.AVAILABLE)
        registered = sum(1 for r in final_results if r.status == DomainStatus.REGISTERED)
        errors = sum(1 for r in final_results if r.status == DomainStatus.ERROR)

        logger.info(
            f"Проверено: {len(final_results)} доменов | "
            f"Свободных: {available} | "
            f"Зарегистрированных: {registered} | "
            f"Ошибок: {errors}"
        )

        return final_results
