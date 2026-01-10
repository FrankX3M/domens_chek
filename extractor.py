"""
Извлечение уникальных корневых доменов из обратных ссылок
"""
import tldextract
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class DomainExtractor:
    """Извлечение уникальных корневых доменов из обратных ссылок"""
    
    def __init__(self):
        # Кэширование tldextract для повышения производительности
        self.tld_extract = tldextract.TLDExtract(
            cache_dir='.tld_cache',
            include_psl_private_domains=True
        )
    
    def extract_unique_domains(self, backlinks: List) -> List:
        """
        Извлечение списка уникальных корневых доменов
        
        Args:
            backlinks: Список обратных ссылок (List[Backlink])
            
        Returns:
            Список уникальных доменов с метаинформацией (List[DomainInfo])
        """
        logger.info(f"Начало извлечения доменов из {len(backlinks)} ссылок")
        
        # Словарь для хранения уникальных доменов
        # Ключ - нормализованный домен, значение - DomainInfo
        unique_domains = {}
        
        for backlink in backlinks:
            if not backlink.source_domain:
                continue
            
            # Извлекаем информацию о домене
            domain_info = self._extract_domain_info(
                backlink.source_domain,
                backlink.dr
            )
            
            # Добавляем или обновляем в словаре
            normalized = domain_info['normalized_domain']
            
            if normalized in unique_domains:
                # Обновляем количество ссылок
                unique_domains[normalized]['backlink_count'] += 1
                
                # Обновляем DR если новый выше
                if domain_info['dr'] is not None:
                    if (unique_domains[normalized]['dr'] is None or
                        domain_info['dr'] > unique_domains[normalized]['dr']):
                        unique_domains[normalized]['dr'] = domain_info['dr']
            else:
                # Добавляем новый домен
                domain_info['backlink_count'] = 1
                unique_domains[normalized] = domain_info
        
        # Конвертируем в список
        result = list(unique_domains.values())
        
        logger.info(
            f"Извлечено {len(result)} уникальных доменов "
            f"из {len(backlinks)} ссылок"
        )
        
        # Статистика
        domains_with_dr = [d for d in result if d['dr'] is not None]
        if domains_with_dr:
            max_dr = max(d['dr'] for d in domains_with_dr)
            avg_dr = sum(d['dr'] for d in domains_with_dr) / len(domains_with_dr)
            logger.info(f"Статистика DR: max={max_dr}, avg={avg_dr:.1f}")
        
        return result
    
    def _extract_domain_info(
        self,
        domain_or_url: str,
        dr: Optional[int] = None
    ) -> dict:
        """
        Извлечение информации о домене из URL или доменного имени
        
        Args:
            domain_or_url: Домен или URL
            dr: Domain Rating (если известен)
            
        Returns:
            Словарь с извлеченной информацией о домене
        """
        # Удаляем пробелы
        domain_or_url = domain_or_url.strip()
        
        # Используем tldextract для корректного парсинга
        extracted = self.tld_extract(domain_or_url)
        
        # Формируем корневой домен
        if extracted.suffix:  # Есть TLD
            normalized = f"{extracted.domain}.{extracted.suffix}"
        else:
            # Fallback для нестандартных случаев
            normalized = extracted.domain
        
        # Нормализуем к нижнему регистру
        normalized = normalized.lower()
        
        return {
            'original_domain': domain_or_url,
            'normalized_domain': normalized,
            'tld': extracted.suffix or '',
            'sld': extracted.domain or '',
            'subdomain': extracted.subdomain or None,
            'dr': dr,
            'backlink_count': 0,
            'is_spam': None,
            'is_registered': None
        }
    
    def get_root_domain(self, domain_or_url: str) -> str:
        """
        Быстрый метод для получения только корневого домена
        
        Args:
            domain_or_url: Домен или URL
            
        Returns:
            Нормализованный корневой домен
        """
        extracted = self.tld_extract(domain_or_url)
        
        if extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}".lower()
        return extracted.domain.lower()
