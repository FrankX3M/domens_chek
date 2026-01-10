"""
Координатор фильтрации и сбора метрик доменов
"""

import asyncio
from typing import List, Dict
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class DomainFilteringPipeline:
    """Координатор фильтрации и сбора метрик"""
    
    def __init__(
        self,
        spam_phrases_file: str = "data/spam_phrases.txt",
        excluded_domains_file: str = "data/excluded_domains.txt",
        enable_spam_filter: bool = True,
        fetch_metrics: bool = True,
        api_client = None
    ):
        """
        Инициализация pipeline фильтрации
        
        Args:
            spam_phrases_file: Путь к файлу со спам-фразами
            excluded_domains_file: Путь к файлу с исключениями
            enable_spam_filter: Включить фильтр спама
            fetch_metrics: Собирать дополнительные метрики
            api_client: Экземпляр API клиента (для сбора метрик)
        """
        from .spam_filter import SpamFilter, DomainExcluder
        from .metrics_collector import DomainMetricsCollector
        
        self.spam_filter = SpamFilter(spam_phrases_file)
        self.domain_excluder = DomainExcluder(excluded_domains_file)
        self.enable_spam_filter = enable_spam_filter
        self.fetch_metrics = fetch_metrics
        
        self.metrics_collector = None
        if fetch_metrics and api_client:
            self.metrics_collector = DomainMetricsCollector(api_client)
    
    async def process_domains(
        self,
        domains: List,
        availability_results: List,
        backlinks: List
    ) -> List:
        """
        Полная обработка доменов: фильтрация + сбор метрик
        
        Args:
            domains: Список уникальных доменов (DomainInfo)
            availability_results: Результаты проверки доступности (DomainCheckResult)
            backlinks: Все обратные ссылки (Backlink) - для фильтрации по анкорам
            
        Returns:
            Список финальных отфильтрованных доменов (FilteredDomain)
        """
        from ..models.filtered_domain import FilteredDomain
        
        logger.info("=" * 70)
        logger.info("Этап 4: Фильтрация и сбор метрик")
        logger.info("=" * 70)
        
        # 1. Загружаем спам-фразы и исключения
        logger.info("Загрузка спам-фраз и исключений...")
        self.spam_filter.load_spam_phrases()
        self.domain_excluder.load_excluded_domains()
        
        # 2. Создаем словарь статусов доступности
        availability_dict = {
            result.domain: result 
            for result in availability_results
        }
        
        # 3. Группируем backlinks по доменам
        domain_backlinks = self._group_backlinks_by_domain(backlinks)
        
        # 4. Обрабатываем каждый домен
        filtered_domains = []
        
        for domain_info in domains:
            # Получаем домен из объекта DomainInfo
            domain = getattr(domain_info, 'normalized_domain', None) or getattr(domain_info, 'domain', str(domain_info))
            
            # Получаем статус доступности
            avail_result = availability_dict.get(domain)
            is_registered = False
            
            if avail_result:
                # Проверяем статус регистрации
                status = getattr(avail_result, 'status', None)
                if status:
                    # Если status - это enum, сравниваем по имени
                    if hasattr(status, 'name'):
                        is_registered = status.name == 'REGISTERED'
                    else:
                        is_registered = str(status).upper() == 'REGISTERED'
            
            # Пропускаем незарегистрированные домены
            if not is_registered:
                logger.debug(f"{domain}: пропущен (не зарегистрирован)")
                continue
            
            # Проверяем исключения
            is_excluded = self.domain_excluder.is_excluded(domain)
            if is_excluded:
                logger.debug(f"{domain}: исключен из списка")
            
            # Фильтруем по спам-анкорам
            domain_links = domain_backlinks.get(domain, [])
            is_spam = False
            spam_examples = []
            
            if self.enable_spam_filter and domain_links:
                is_spam = any(
                    self.spam_filter.is_spam_anchor(
                        getattr(bl, 'anchor_text', None)
                    )
                    for bl in domain_links
                )
                
                if is_spam:
                    spam_examples = self.spam_filter.get_spam_examples(
                        domain_links,
                        max_examples=3
                    )
                    logger.debug(
                        f"{domain}: помечен как спам "
                        f"(примеры: {spam_examples[:2]})"
                    )
            
            # Получаем DR из domain_info если доступен
            dr = getattr(domain_info, 'dr', None)
            ur = getattr(domain_info, 'ur', None)
            
            # Создаем объект FilteredDomain
            filtered_domain = FilteredDomain(
                domain=domain,
                backlink_count=len(domain_links),
                dr=dr,
                ur=ur,
                is_registered=is_registered,
                is_spam=is_spam,
                is_excluded=is_excluded,
                spam_anchor_examples=spam_examples,
                checked_at=datetime.now()
            )
            
            filtered_domains.append(filtered_domain)
        
        logger.info(f"Обработано доменов: {len(filtered_domains)}")
        
        # 5. Собираем дополнительные метрики (опционально)
        if self.fetch_metrics and self.metrics_collector:
            logger.info("")
            logger.info("Сбор дополнительных метрик...")
            
            # Собираем метрики только для валидных доменов
            valid_domains = [
                d.domain for d in filtered_domains 
                if d.is_valid
            ]
            
            if valid_domains:
                metrics = await self.metrics_collector.collect_metrics(
                    valid_domains
                )
                
                # Обновляем объекты FilteredDomain
                for filtered_domain in filtered_domains:
                    if filtered_domain.domain in metrics:
                        domain_metrics = metrics[filtered_domain.domain]
                        if domain_metrics:
                            filtered_domain.dr = domain_metrics.get("dr")
                            filtered_domain.ur = domain_metrics.get("ur")
                            filtered_domain.total_backlinks = domain_metrics.get("total_backlinks")
                            filtered_domain.referring_domains = domain_metrics.get("referring_domains")
                            filtered_domain.organic_traffic = domain_metrics.get("organic_traffic")
        
        # Статистика
        self._log_statistics(filtered_domains)
        
        return filtered_domains
    
    def _group_backlinks_by_domain(
        self,
        backlinks: List
    ) -> Dict[str, List]:
        """Группировка обратных ссылок по доменам"""
        grouped = defaultdict(list)
        
        for backlink in backlinks:
            # Получаем домен из объекта Backlink
            source_domain = getattr(backlink, 'source_domain', None)
            
            if source_domain:
                grouped[source_domain.lower()].append(backlink)
        
        return dict(grouped)
    
    def _log_statistics(self, domains: List) -> None:
        """Логирование статистики"""
        total = len(domains)
        if total == 0:
            logger.info("=" * 50)
            logger.info("Нет доменов для обработки")
            logger.info("=" * 50)
            return
        
        valid = sum(1 for d in domains if d.is_valid)
        spam = sum(1 for d in domains if d.is_spam)
        excluded = sum(1 for d in domains if d.is_excluded)
        
        logger.info("=" * 50)
        logger.info("Статистика фильтрации:")
        logger.info(f"  Всего доменов: {total}")
        logger.info(f"  Валидные: {valid} ({valid/total*100:.1f}%)")
        logger.info(f"  Спам: {spam} ({spam/total*100:.1f}%)")
        logger.info(f"  Исключенные: {excluded} ({excluded/total*100:.1f}%)")
        logger.info("=" * 50)


# Экспорт основных классов
__all__ = [
    'DomainFilteringPipeline',
]
