import aiohttp
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)


class RDAPBootstrapLoader:
    """Загрузка и кэширование IANA RDAP Bootstrap Registry"""
    
    def __init__(
        self,
        cache_file: str = "data/rdap_bootstrap.json",
        cache_ttl_days: int = 7,
        bootstrap_url: str = "https://data.iana.org/rdap/dns.json"
    ):
        self.cache_file = Path(cache_file)
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.bootstrap_url = bootstrap_url
        
        # Данные bootstrap
        self._tld_to_servers: Dict[str, list] = {}
        self._loaded = False
    
    async def load(self) -> None:
        """Загрузка bootstrap данных (из кэша или с сервера)"""
        if self._loaded:
            return
        
        # Проверяем кэш
        if await self._is_cache_valid():
            logger.info("Загрузка RDAP bootstrap из кэша...")
            await self._load_from_cache()
        else:
            logger.info("Загрузка RDAP bootstrap с IANA...")
            await self._load_from_server()
        
        self._loaded = True
        logger.info(
            f"RDAP bootstrap загружен: {len(self._tld_to_servers)} TLD "
            f"поддерживают RDAP"
        )
    
    async def _is_cache_valid(self) -> bool:
        """Проверка валидности кэша"""
        if not self.cache_file.exists():
            return False
        
        # Проверяем возраст файла
        mtime = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        age = datetime.now() - mtime
        return age < self.cache_ttl
    
    async def _load_from_cache(self) -> None:
        """Загрузка из кэша"""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            self._tld_to_servers = data.get('tld_to_servers', {})
        except Exception as e:
            logger.warning(f"Ошибка загрузки кэша: {e}. Загрузка с сервера...")
            await self._load_from_server()
    
    async def _load_from_server(self) -> None:
        """Загрузка с IANA сервера"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.bootstrap_url) as response:
                    if response.status != 200:
                        raise Exception(
                            f"HTTP {response.status}: {await response.text()}"
                        )
                    
                    data = await response.json()
            
            # Парсинг данных
            self._parse_bootstrap_data(data)
            
            # Сохранение в кэш
            await self._save_to_cache()
            
        except Exception as e:
            logger.error(f"Ошибка загрузки RDAP bootstrap: {e}")
            # Попытка использовать старый кэш
            if self.cache_file.exists():
                logger.warning("Использование устаревшего кэша...")
                await self._load_from_cache()
            else:
                raise
    
    def _parse_bootstrap_data(self, data: dict) -> None:
        """Парсинг JSON данных bootstrap"""
        services = data.get('services', [])
        self._tld_to_servers = {}
        
        for service in services:
            if len(service) < 2:
                continue
            
            tlds = service[0]  # Список TLD
            servers = service[1]  # Список RDAP серверов
            
            for tld in tlds:
                # Удаляем точку в начале если есть
                tld = tld.lstrip('.')
                self._tld_to_servers[tld.lower()] = servers
    
    async def _save_to_cache(self) -> None:
        """Сохранение в кэш"""
        try:
            # Создаем директорию если не существует
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'tld_to_servers': self._tld_to_servers,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"RDAP bootstrap сохранен в {self.cache_file}")
        except Exception as e:
            logger.warning(f"Не удалось сохранить кэш: {e}")
    
    def get_rdap_servers(self, tld: str) -> Optional[list]:
        """
        Получение RDAP серверов для TLD
        
        Args:
            tld: Top-level domain (com, co.uk, etc)
        
        Returns:
            Список URLs RDAP серверов или None если не поддерживается
        """
        if not self._loaded:
            logger.warning("Bootstrap не загружен! Вызовите load() сначала.")
            return None
        
        return self._tld_to_servers.get(tld.lower())
    
    def supports_rdap(self, tld: str) -> bool:
        """Проверка поддержки RDAP для TLD"""
        return tld.lower() in self._tld_to_servers
    
    def get_supported_tlds(self) -> Set[str]:
        """Получение всех TLD с поддержкой RDAP"""
        return set(self._tld_to_servers.keys())
