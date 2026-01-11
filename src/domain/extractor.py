"""
Domain Extractor
Извлечение уникальных доменов из списка обратных ссылок
"""

import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class DomainExtractor:
    """Извлечение уникальных доменов из backlinks"""
    
    def __init__(self):
        """Инициализация экстрактора"""
        logger.info("Domain Extractor инициализирован")
    
    def extract_unique_domains(
        self,
        backlinks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Извлечение уникальных доменов из списка ссылок

        Args:
            backlinks: Список ссылок от Keys.so API (backlinks или outlinks)

        Returns:
            Список уникальных доменов
        """
        logger.info(f"Извлечение доменов из {len(backlinks)} ссылок")

        unique_domains: Set[str] = set()

        for link in backlinks:
            # Keys.so API возвращает домен в разных полях:
            # - backlinks (входящие): 'source_name' - домен источника
            # - outlinks (исходящие): 'name' - домен назначения
            domain = link.get('source_name') or link.get('name')

            if domain and isinstance(domain, str):
                # Очистка домена (удаление www. если есть)
                domain = domain.lower().strip()
                if domain.startswith('www.'):
                    domain = domain[4:]

                # Проверка, что это валидный домен (содержит точку)
                if '.' not in domain or len(domain) <= 3:
                    continue

                # Фильтрация поддоменов (например, blog.example.com -> пропускаем)
                # Оставляем только домены второго уровня (example.com)
                parts = domain.split('.')
                if len(parts) > 2:
                    # Проверяем на известные TLD второго уровня (co.uk, com.au и т.д.)
                    if len(parts) == 3 and parts[1] in ['co', 'com', 'org', 'net', 'ac', 'gov']:
                        # Это нормальный домен типа example.co.uk
                        unique_domains.add(domain)
                    # Иначе это поддомен - пропускаем
                elif len(parts) == 2:
                    # Обычный домен второго уровня
                    unique_domains.add(domain)

        result = sorted(list(unique_domains))
        logger.info(f"Найдено уникальных доменов: {len(result)}")

        return result
