from dataclasses import dataclass, field
from typing import List, Optional
from .backlink import Backlink


@dataclass
class DomainData:
    """Полные данные о домене"""
    domain: str
    backlinks: List[Backlink] = field(default_factory=list)
    total_backlinks: int = 0
    unique_domains: int = 0
    
    # Статистика (будет заполняться на следующих этапах)
    max_dr: Optional[int] = None
    avg_dr: Optional[float] = None
    spam_free_domains: int = 0
    registered_domains: int = 0
