import aiosqlite
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..models.domain_status import DomainCheckResult, DomainStatus, CheckMethod

logger = logging.getLogger(__name__)


class DomainCacheManager:
    """Управление кэшированием результатов проверки доменов"""
    
    def __init__(
        self,
        db_path: str = "data/domain_cache.db",
        ttl_days: int = 7
    ):
        self.db_path = Path(db_path)
        self.ttl = timedelta(days=ttl_days)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Инициализация базы данных"""
        if self._initialized:
            return
        
        # Создаем директорию если не существует
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем таблицу
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS domain_checks (
                    domain TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    check_method TEXT NOT NULL,
                    checked_at TIMESTAMP NOT NULL,
                    tld_supports_rdap BOOLEAN DEFAULT 0,
                    registrar TEXT,
                    error_message TEXT
                )
            ''')
            
            # Индекс для быстрого поиска устаревших записей
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_checked_at 
                ON domain_checks(checked_at)
            ''')
            
            await db.commit()
        
        self._initialized = True
        logger.info(f"Кэш доменов инициализирован: {self.db_path}")
    
    async def get(self, domain: str) -> Optional[DomainCheckResult]:
        """
        Получение результата из кэша
        
        Args:
            domain: Доменное имя
        
        Returns:
            DomainCheckResult если есть в кэше и не устарел, иначе None
        """
        if not self._initialized:
            await self.initialize()
        
        domain = domain.lower()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM domain_checks WHERE domain = ?',
                (domain,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                # Проверяем возраст записи
                checked_at = datetime.fromisoformat(row['checked_at'])
                age = datetime.now() - checked_at
                
                if age > self.ttl:
                    logger.debug(f"Кэш для {domain} устарел ({age.days} дней)")
                    return None
                
                # Возвращаем результат
                return DomainCheckResult(
                    domain=row['domain'],
                    status=DomainStatus(row['status']),
                    check_method=CheckMethod.CACHE,  # Помечаем что из кэша
                    checked_at=checked_at,
                    tld_supports_rdap=bool(row['tld_supports_rdap']),
                    error_message=row['error_message'],
                    registrar=row['registrar']
                )
    
    async def set(self, result: DomainCheckResult) -> None:
        """
        Сохранение результата в кэш
        
        Args:
            result: Результат проверки домена
        """
        if not self._initialized:
            await self.initialize()
        
        domain = result.domain.lower()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO domain_checks 
                (domain, status, check_method, checked_at, tld_supports_rdap, registrar, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                domain,
                result.status.value,
                result.check_method.value,
                result.checked_at.isoformat(),
                result.tld_supports_rdap,
                result.registrar,
                result.error_message
            ))
            await db.commit()
        
        logger.debug(f"Результат для {domain} сохранен в кэш")
    
    async def cleanup_old_entries(self) -> int:
        """
        Очистка устаревших записей из кэша
        
        Returns:
            Количество удаленных записей
        """
        if not self._initialized:
            await self.initialize()
        
        cutoff_date = (datetime.now() - self.ttl).isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'DELETE FROM domain_checks WHERE checked_at < ?',
                (cutoff_date,)
            )
            deleted_count = cursor.rowcount
            await db.commit()
        
        if deleted_count > 0:
            logger.info(f"Удалено {deleted_count} устаревших записей из кэша")
        
        return deleted_count
