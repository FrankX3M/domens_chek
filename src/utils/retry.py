import asyncio
import logging
from functools import wraps
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_failure(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exponential: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Декоратор для повторных попыток выполнения асинхронной функции
    
    Args:
        max_attempts: Максимальное количество попыток
        base_delay: Базовая задержка между попытками (сек)
        exponential: Использовать экспоненциальную задержку
        exceptions: Кортеж исключений для обработки
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__}: все {max_attempts} попытки "
                            f"исчерпаны. Последняя ошибка: {e}"
                        )
                        raise
                    
                    # Вычисляем задержку
                    if exponential:
                        delay = base_delay * (2 ** (attempt - 1))
                    else:
                        delay = base_delay
                    
                    logger.warning(
                        f"{func.__name__}: попытка {attempt}/{max_attempts} "
                        f"не удалась ({type(e).__name__}: {e}). "
                        f"Повтор через {delay:.1f}s..."
                    )
                    
                    await asyncio.sleep(delay)
            
            # На случай если цикл завершился без return
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator
