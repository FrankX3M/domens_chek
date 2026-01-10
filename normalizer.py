"""
Нормализация доменов
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DomainNormalizer:
    """Нормализация доменов"""
    
    # Константы
    PREFIXES_TO_REMOVE = ['www.', 'ww2.', 'ww3.', 'm.', 'mobile.']
    PROTOCOLS = ['http://', 'https://', 'ftp://', 'ftps://']
    
    @classmethod
    def normalize(cls, domain: str) -> str:
        """
        Полная нормализация домена
        
        Args:
            domain: Исходный домен или URL
            
        Returns:
            Нормализованный домен
        """
        if not domain:
            return ""
        
        # 1. Удаляем протоколы
        normalized = cls._remove_protocol(domain)
        
        # 2. Удаляем путь после домена
        normalized = cls._remove_path(normalized)
        
        # 3. Удаляем порт
        normalized = cls._remove_port(normalized)
        
        # 4. Удаляем известные префиксы (www, m, etc)
        normalized = cls._remove_prefixes(normalized)
        
        # 5. К нижнему регистру
        normalized = normalized.lower().strip()
        
        return normalized
    
    @classmethod
    def _remove_protocol(cls, url: str) -> str:
        """Удаление протокола из URL"""
        for protocol in cls.PROTOCOLS:
            if url.startswith(protocol):
                return url[len(protocol):]
        return url
    
    @classmethod
    def _remove_path(cls, url: str) -> str:
        """Удаление пути после доменного имени"""
        # Находим первый слэш после домена
        slash_pos = url.find('/')
        if slash_pos != -1:
            return url[:slash_pos]
        return url
    
    @classmethod
    def _remove_port(cls, domain: str) -> str:
        """Удаление порта из домена"""
        # Ищем двоеточие (но не в IPv6)
        if ':' in domain and not domain.startswith('['):
            return domain.split(':')[0]
        return domain
    
    @classmethod
    def _remove_prefixes(cls, domain: str) -> str:
        """Удаление известных префиксов"""
        for prefix in cls.PREFIXES_TO_REMOVE:
            if domain.startswith(prefix):
                return domain[len(prefix):]
        return domain
    
    @classmethod
    def is_valid_domain(cls, domain: str) -> bool:
        """
        Проверка валидности доменного имени
        
        Args:
            domain: Доменное имя
            
        Returns:
            True если домен валиден
        """
        if not domain or len(domain) > 255:
            return False
        
        # Регулярка для проверки формата домена
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9]'  # Первый символ - буква или цифра
            r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Последующие части
            r'+[a-zA-Z]{2,}$'  # TLD (минимум 2 символа)
        )
        
        return bool(domain_pattern.match(domain))
