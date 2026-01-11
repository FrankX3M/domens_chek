from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class FilteredDomain:
    """Модель отфильтрованного домена с метриками"""
    
    # Основная информация
    domain: str
    
    # Метрики
    dr: Optional[int] = None  # Domain Rating
    ur: Optional[int] = None  # URL Rating
    backlink_count: int = 0
    total_backlinks: Optional[int] = None
    referring_domains: Optional[int] = None
    organic_traffic: Optional[int] = None
    
    # Статусы
    is_registered: bool = True
    is_spam: bool = False
    is_excluded: bool = False
    availability_status: Optional[str] = None  # "AVAILABLE", "REGISTERED", "ERROR"
    
    # Дополнительная информация
    spam_anchor_examples: List[str] = field(default_factory=list)
    checked_at: Optional[datetime] = None
    
    @property
    def is_valid(self) -> bool:
        """Проверка, что домен валиден для отчета"""
        return (
            not self.is_spam and
            not self.is_excluded
        )
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            "domain": self.domain,
            "dr": self.dr,
            "ur": self.ur,
            "backlink_count": self.backlink_count,
            "total_backlinks": self.total_backlinks,
            "referring_domains": self.referring_domains,
            "organic_traffic": self.organic_traffic,
            "is_registered": self.is_registered,
            "is_spam": self.is_spam,
            "is_excluded": self.is_excluded,
            "availability_status": self.availability_status,
            "spam_anchor_examples": self.spam_anchor_examples,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None
        }
