class APIError(Exception):
    """Базовая ошибка API"""
    pass


class AuthenticationError(APIError):
    """Ошибка авторизации"""
    pass


class RateLimitError(APIError):
    """Превышен лимит запросов"""
    pass


class NetworkError(APIError):
    """Ошибка сети"""
    pass
