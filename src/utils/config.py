"""
Configuration Management
Управление конфигурацией приложения
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class APIConfig:
    """Конфигурация API"""
    api_key: str
    base_url: str = "https://api.keys.so/v1"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "APIConfig":
        """Загрузка конфигурации из переменных окружения"""
        api_key = os.getenv("KEYS_SO_API_KEY")
        if not api_key:
            raise ValueError(
                "KEYS_SO_API_KEY не установлен. "
                "Установите переменную окружения или создайте .env файл"
            )
        
        return cls(
            api_key=api_key,
            base_url=os.getenv("KEYS_SO_BASE_URL", cls.base_url),
            timeout=int(os.getenv("REQUEST_TIMEOUT", cls.timeout)),
            max_retries=int(os.getenv("MAX_RETRIES", cls.max_retries))
        )


@dataclass
class LogConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "LogConfig":
        """Загрузка конфигурации логирования из переменных окружения"""
        return cls(
            level=os.getenv("LOG_LEVEL", cls.level),
            file=os.getenv("LOG_FILE")
        )


@dataclass
class AppConfig:
    """Общая конфигурация приложения"""
    api: APIConfig
    log: LogConfig
    max_concurrent: int = 20
    output_dir: str = "output"
    data_dir: str = "data"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Загрузка полной конфигурации из переменных окружения"""
        return cls(
            api=APIConfig.from_env(),
            log=LogConfig.from_env(),
            max_concurrent=int(os.getenv("MAX_CONCURRENT_REQUESTS", 20)),
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            data_dir=os.getenv("DATA_DIR", "data")
        )
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
