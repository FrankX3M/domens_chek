from dataclasses import dataclass
from typing import Optional


@dataclass
class DomainInfo:
    """Информация о домене из обратных ссылок"""
    normalized_domain: str  # Нормализованный домен (example.com)
    original_url: str  # Оригинальный URL из которого извлечен домен
    tld: str  # Top-level domain (com, org, etc)
    
    # Дополнительные поля (для будущих этапов)
    is_subdomain: bool = False
    subdomain: Optional[str] = None
