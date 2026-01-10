"""
Сбор детальных метрик доменов через API keys.so
"""

import asyncio
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DomainMetricsCollector:
    """Сбор детальных метрик доменов через API keys.so"""
    
    def __init__(
        self,
        api_client,
        max_concurrent: int = 10
    ):
        """
        Инициализация сборщика метрик
        
        Args:
            api_client: Экземпляр KeysSoClient
            max_concurrent: Максимум параллельных запросов
        """
        self.api_client = api_client
        self.max_concurrent = max_concurrent
    
    async def collect_metrics(
        self,
        domains: List[str]
    ) -> Dict[str, Dict[str, any]]:
        """
        Сбор метрик для списка доменов
        
        Args:
            domains: Список доменов
            
        Returns:
            Словарь {домен: метрики}
        """
        logger.info(f"Начало сбора метрик для {len(domains)} доменов...")
        
        # Семафор для ограничения concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Запускаем параллельный сбор
        tasks = [
            self._get_domain_metrics_with_semaphore(domain, semaphore)
            for domain in domains
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Формируем словарь результатов
        metrics_dict = {}
        for domain, result in zip(domains, results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка сбора метрик для {domain}: {result}")
                metrics_dict[domain] = None
            else:
                metrics_dict[domain] = result
        
        successful = sum(1 for v in metrics_dict.values() if v is not None)
        logger.info(
            f"Сбор метрик завершен: {successful}/{len(domains)} успешно"
        )
        
        return metrics_dict
    
    async def _get_domain_metrics_with_semaphore(
        self,
        domain: str,
        semaphore: asyncio.Semaphore
    ) -> Optional[Dict[str, any]]:
        """Получение метрик с учетом semaphore"""
        async with semaphore:
            return await self._get_domain_metrics(domain)
    
    async def _get_domain_metrics(
        self,
        domain: str
    ) -> Optional[Dict[str, any]]:
        """
        Получение метрик одного домена
        
        Args:
            domain: Доменное имя
            
        Returns:
            Словарь с метриками или None при ошибке
        """
        try:
            # Запрос к API keys.so для получения метрик домена
            # ПРИМЕЧАНИЕ: Структура эндпоинта может отличаться - адаптировать под реальный API
            # Пример реального запроса нужно уточнить в документации API
            
            # Вариант 1: Если есть отдельный эндпоинт для метрик домена
            response = await self.api_client._make_request(
                method="GET",
                endpoint="/domain/metrics",
                params={"domain": domain}
            )
            
            # Парсинг ответа
            metrics = {
                "dr": response.get("domain_rating"),
                "ur": response.get("url_rating"),
                "total_backlinks": response.get("total_backlinks"),
                "referring_domains": response.get("referring_domains"),
                "organic_traffic": response.get("organic_traffic")
            }
            
            logger.debug(
                f"{domain}: DR={metrics['dr']}, "
                f"backlinks={metrics['total_backlinks']}"
            )
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Не удалось получить метрики для {domain}: {e}")
            return None
    
    async def collect_metrics_batch(
        self,
        domains: List[str],
        batch_size: int = 100
    ) -> Dict[str, Dict[str, any]]:
        """
        Сбор метрик пакетами для больших списков доменов
        
        Args:
            domains: Список доменов
            batch_size: Размер пакета
            
        Returns:
            Словарь {домен: метрики}
        """
        logger.info(
            f"Начало пакетного сбора метрик для {len(domains)} доменов "
            f"(размер пакета: {batch_size})..."
        )
        
        all_metrics = {}
        
        # Разбиваем на пакеты
        for i in range(0, len(domains), batch_size):
            batch = domains[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(domains) + batch_size - 1) // batch_size
            
            logger.info(
                f"Обработка пакета {batch_num}/{total_batches} "
                f"({len(batch)} доменов)..."
            )
            
            # Собираем метрики для текущего пакета
            batch_metrics = await self.collect_metrics(batch)
            all_metrics.update(batch_metrics)
            
            # Небольшая задержка между пакетами
            if i + batch_size < len(domains):
                await asyncio.sleep(1)
        
        return all_metrics
    
    def get_metrics_summary(
        self,
        metrics_dict: Dict[str, Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Получение сводной статистики по метрикам
        
        Args:
            metrics_dict: Словарь с метриками доменов
            
        Returns:
            Сводная статистика
        """
        valid_metrics = [m for m in metrics_dict.values() if m is not None]
        
        if not valid_metrics:
            return {
                "total_domains": len(metrics_dict),
                "successful": 0,
                "failed": len(metrics_dict)
            }
        
        # Собираем статистику по DR
        dr_values = [m["dr"] for m in valid_metrics if m.get("dr") is not None]
        
        summary = {
            "total_domains": len(metrics_dict),
            "successful": len(valid_metrics),
            "failed": len(metrics_dict) - len(valid_metrics),
        }
        
        if dr_values:
            summary.update({
                "avg_dr": sum(dr_values) / len(dr_values),
                "min_dr": min(dr_values),
                "max_dr": max(dr_values),
                "median_dr": sorted(dr_values)[len(dr_values) // 2]
            })
        
        return summary
