"""
Domain Filtering Pipeline
Пайплайн для фильтрации доменов и сбора метрик
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.filtered_domain import FilteredDomain
from ..availability.checker import AvailabilityResult

logger = logging.getLogger(__name__)


class DomainFilteringPipeline:
    """Пайплайн для фильтрации доменов"""
    
    def __init__(
        self,
        spam_phrases_file: str = "data/spam_phrases.txt",
        excluded_domains_file: str = "data/excluded_domains.txt",
        fetch_metrics: bool = True,
        api_client: Optional[Any] = None
    ):
        """
        Инициализация пайплайна
        
        Args:
            spam_phrases_file: Путь к файлу со спам-фразами
            excluded_domains_file: Путь к файлу с исключениями
            fetch_metrics: Собирать ли дополнительные метрики
            api_client: API клиент для получения метрик
        """
        self.spam_phrases_file = spam_phrases_file
        self.excluded_domains_file = excluded_domains_file
        self.fetch_metrics = fetch_metrics
        self.api_client = api_client
        
        # Загрузка спам-фраз
        self.spam_phrases = self._load_spam_phrases()
        
        # Загрузка исключенных доменов
        self.excluded_domains = self._load_excluded_domains()
        
        logger.info(
            f"Filtering Pipeline инициализирован "
            f"(spam_phrases={len(self.spam_phrases)}, "
            f"excluded={len(self.excluded_domains)})"
        )
    
    def _load_spam_phrases(self) -> List[str]:
        """Загрузка спам-фраз из файла"""
        try:
            path = Path(self.spam_phrases_file)
            if not path.exists():
                logger.warning(f"Файл спам-фраз не найден: {path}")
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                phrases = [
                    line.strip().lower()
                    for line in f
                    if line.strip() and not line.startswith('#')
                ]
            
            logger.info(f"Загружено {len(phrases)} спам-фраз")
            return phrases
            
        except Exception as e:
            logger.error(f"Ошибка загрузки спам-фраз: {e}")
            return []
    
    def _load_excluded_domains(self) -> List[str]:
        """Загрузка исключенных доменов из файла"""
        try:
            path = Path(self.excluded_domains_file)
            if not path.exists():
                logger.warning(f"Файл исключений не найден: {path}")
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                domains = [
                    line.strip().lower()
                    for line in f
                    if line.strip() and not line.startswith('#')
                ]
            
            logger.info(f"Загружено {len(domains)} исключенных доменов")
            return domains
            
        except Exception as e:
            logger.error(f"Ошибка загрузки исключений: {e}")
            return []
    
    async def process_domains(
        self,
        domains: List[str],
        availability_results: List[AvailabilityResult],
        backlinks: List[Dict[str, Any]]
    ) -> List[FilteredDomain]:
        """
        Обработка доменов через пайплайн
        
        Args:
            domains: Список доменов
            availability_results: Результаты проверки доступности
            backlinks: Список обратных ссылок
            
        Returns:
            Список отфильтрованных доменов с метриками
        """
        logger.info(f"Обработка {len(domains)} доменов через пайплайн")
        
        # Создаем словарь для быстрого поиска availability
        availability_map = {
            result.domain: result
            for result in availability_results
        }
        
        # Создаем словарь для подсчета backlinks
        backlink_counts = {}
        for backlink in backlinks:
            domain = backlink.get('domain', '')
            backlink_counts[domain] = backlink_counts.get(domain, 0) + 1
        
        # Обрабатываем каждый домен
        filtered_domains = []
        
        for domain in domains:
            # Получаем availability
            availability = availability_map.get(domain)
            if not availability:
                continue
            
            # Создаем FilteredDomain
            filtered_domain = FilteredDomain(
                domain=domain,
                is_registered=(
                    availability.status.value == "REGISTERED"
                    if availability else False
                ),
                backlink_count=backlink_counts.get(domain, 0)
            )
            
            # Проверка на исключенные домены
            if domain.lower() in self.excluded_domains:
                filtered_domain.is_excluded = True
            
            # TODO: Проверка на спам в анкорах
            # TODO: Получение метрик через API
            
            filtered_domains.append(filtered_domain)
        
        logger.info(
            f"Обработано доменов: {len(filtered_domains)}, "
            f"валидных: {sum(1 for d in filtered_domains if d.is_valid)}"
        )
        
        return filtered_domains
