"""
Модель данных для обработанного домена
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DomainInfo:
    """Информация об обработанном домене"""
    original_domain: str       # Исходный домен из backlink
    normalized_domain: str     # Нормализованный корневой домен
    tld: str                   # Top-level domain (com, co.uk, etc)
    sld: str                   # Second-level domain (example)
    subdomain: Optional[str]   # Поддомен (blog, www, etc)
    
    # Метрики (будут заполняться на следующих этапах)
    dr: Optional[int] = None
    backlink_count: int = 0
    is_spam: Optional[bool] = None
    is_registered: Optional[bool] = None
    
    def __str__(self) -> str:
        """Строковое представление домена"""
        return (
            f"{self.normalized_domain} "
            f"(ссылок: {self.backlink_count}, "
            f"DR: {self.dr if self.dr else 'N/A'})"
        )
    
    def __repr__(self) -> str:
        """Техническое представление для отладки"""
        return (
            f"DomainInfo(normalized='{self.normalized_domain}', "
            f"backlinks={self.backlink_count}, dr={self.dr})"
        )
