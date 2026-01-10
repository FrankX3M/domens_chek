"""
Модель финального отфильтрованного домена
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class FilteredDomain:
    """Финальная модель домена после всех проверок"""
    domain: str
    
    # Базовые метрики (из Этапа 2)
    backlink_count: int = 0
    dr: Optional[int] = None
    ur: Optional[int] = None
    
    # Статусы проверок
    is_registered: bool = True  # Из Этапа 3
    is_spam: bool = False  # Из Этапа 4
    is_excluded: bool = False  # Из Этапа 4
    
    # Дополнительные метрики (если собраны)
    total_backlinks: Optional[int] = None
    referring_domains: Optional[int] = None
    organic_traffic: Optional[int] = None
    
    # Детали анкоров
    spam_anchor_examples: list = field(default_factory=list)
    
    # Метаданные
    checked_at: Optional[datetime] = None
    
    @property
    def is_valid(self) -> bool:
        """Домен валиден для финального отчета"""
        return (
            self.is_registered and 
            not self.is_spam and 
            not self.is_excluded
        )
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для экспорта"""
        return {
            'domain': self.domain,
            'backlink_count': self.backlink_count,
            'dr': self.dr,
            'ur': self.ur,
            'is_registered': self.is_registered,
            'is_spam': self.is_spam,
            'is_excluded': self.is_excluded,
            'is_valid': self.is_valid,
            'total_backlinks': self.total_backlinks,
            'referring_domains': self.referring_domains,
            'organic_traffic': self.organic_traffic,
            'spam_anchor_examples': self.spam_anchor_examples,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }
    
    def __str__(self) -> str:
        """Строковое представление"""
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        flags = []
        if self.is_spam:
            flags.append("SPAM")
        if self.is_excluded:
            flags.append("EXCLUDED")
        if not self.is_registered:
            flags.append("UNREGISTERED")
        
        flags_str = f" [{', '.join(flags)}]" if flags else ""
        
        return (
            f"{status} {self.domain} "
            f"(DR: {self.dr if self.dr else 'N/A'}, "
            f"Links: {self.backlink_count}){flags_str}"
        )
