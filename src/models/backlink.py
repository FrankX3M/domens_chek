from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Backlink:
    """Модель обратной ссылки"""
    source_url: str           # URL источника ссылки
    target_url: str           # URL цели (наш домен)
    source_domain: str        # Домен источника
    anchor_text: Optional[str] = None  # Текст анкора
    dr: Optional[int] = None  # Domain Rating источника
    ur: Optional[int] = None  # URL Rating
    discovered_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Нормализация данных после инициализации"""
        if self.source_domain:
            self.source_domain = self.source_domain.lower().strip()
