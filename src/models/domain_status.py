from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class DomainStatus(Enum):
    """Статус доступности домена"""
    REGISTERED = "REGISTERED"
    AVAILABLE = "AVAILABLE"
    UNKNOWN = "UNKNOWN"


class CheckMethod(Enum):
    """Метод проверки домена"""
    RDAP = "RDAP"
    WHOIS_API = "WHOIS_API"
    WHOIS_LOCAL = "WHOIS_LOCAL"
    CACHE = "CACHE"


@dataclass
class DomainCheckResult:
    """Результат проверки домена"""
    domain: str
    status: DomainStatus
    check_method: CheckMethod
    checked_at: datetime
    tld_supports_rdap: bool = False
    error_message: Optional[str] = None
    
    # WHOIS данные (опционально)
    registrar: Optional[str] = None
    creation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
