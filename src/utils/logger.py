"""
Logger Setup
Настройка системы логирования
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import LogConfig


def setup_logger(
    config: Optional[LogConfig] = None,
    name: Optional[str] = None
) -> logging.Logger:
    """
    Настройка логгера
    
    Args:
        config: Конфигурация логирования
        name: Имя логгера (по умолчанию root)
        
    Returns:
        Настроенный логгер
    """
    if config is None:
        config = LogConfig()
    
    # Получаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.level.upper()))
    
    # Удаляем существующие обработчики
    logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(config.format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (если указан)
    if config.file:
        file_path = Path(config.file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, config.level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получение логгера по имени
    
    Args:
        name: Имя модуля
        
    Returns:
        Логгер
    """
    return logging.getLogger(name)
