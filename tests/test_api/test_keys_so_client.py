import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.keys_so_client import KeysSoClient
from src.api.exceptions import APIError, AuthenticationError, RateLimitError
from src.models.backlink import Backlink


@pytest.mark.asyncio
async def test_client_initialization():
    """Тест инициализации клиента"""
    client = KeysSoClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.keys.so/v1"
    assert client.max_retries == 3
    assert client.batch_size == 100000


@pytest.mark.asyncio
async def test_client_context_manager():
    """Тест использования клиента как context manager"""
    async with KeysSoClient(api_key="test_key") as client:
        assert client.session is not None
    # После выхода из контекста сессия должна быть закрыта


@pytest.mark.asyncio
async def test_authentication_error():
    """Тест обработки ошибки авторизации"""
    client = KeysSoClient(api_key="invalid_key")
    
    # Mock HTTP ответ с 401 статусом
    mock_response = MagicMock()
    mock_response.status = 401
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    with patch.object(client, 'session') as mock_session:
        mock_session.request = MagicMock(return_value=mock_response)
        
        # Проверка что выбрасывается AuthenticationError
        with pytest.raises(AuthenticationError):
            await client._make_request("GET", "/backlinks")


@pytest.mark.asyncio
async def test_rate_limit_error():
    """Тест обработки rate limit"""
    client = KeysSoClient(api_key="test_key")
    
    # Mock HTTP ответ с 429 статусом
    mock_response = MagicMock()
    mock_response.status = 429
    mock_response.headers = {'Retry-After': '60'}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    with patch.object(client, 'session') as mock_session:
        mock_session.request = MagicMock(return_value=mock_response)
        
        # Проверка что выбрасывается RateLimitError
        with pytest.raises(RateLimitError):
            await client._make_request("GET", "/backlinks")


@pytest.mark.asyncio
async def test_get_backlinks_success():
    """Тест успешного получения обратных ссылок"""
    client = KeysSoClient(api_key="test_key")
    
    # Mock успешного ответа
    mock_response_data = {
        'backlinks': [
            {
                'source_url': 'https://example.com/page1',
                'target_url': 'https://target.com',
                'source_domain': 'example.com',
                'anchor_text': 'click here',
                'dr': 45,
                'ur': 32,
                'discovered_at': '2025-01-10T10:00:00Z'
            },
            {
                'source_url': 'https://test.com/page2',
                'target_url': 'https://target.com',
                'source_domain': 'test.com',
                'dr': 60,
                'ur': 50
            }
        ],
        'total': 2
    }
    
    with patch.object(client, '_make_request', new=AsyncMock(return_value=mock_response_data)):
        backlinks = await client.get_backlinks("target.com", limit=10)
        
        assert len(backlinks) == 2
        assert isinstance(backlinks[0], Backlink)
        assert backlinks[0].source_domain == "example.com"
        assert backlinks[0].dr == 45
        assert backlinks[1].source_domain == "test.com"
        assert backlinks[1].dr == 60


@pytest.mark.asyncio
async def test_parse_backlink():
    """Тест парсинга обратной ссылки"""
    client = KeysSoClient(api_key="test_key")
    
    data = {
        'source_url': 'https://example.com/page',
        'target_url': 'https://target.com',
        'source_domain': 'example.com',
        'anchor_text': 'test link',
        'dr': 55,
        'ur': 40,
        'discovered_at': '2025-01-10T12:00:00Z'
    }
    
    backlink = client._parse_backlink(data, "target.com")
    
    assert isinstance(backlink, Backlink)
    assert backlink.source_url == 'https://example.com/page'
    assert backlink.source_domain == 'example.com'
    assert backlink.dr == 55
    assert backlink.anchor_text == 'test link'
    assert backlink.discovered_at is not None


@pytest.mark.asyncio
async def test_pagination():
    """Тест обработки пагинации"""
    client = KeysSoClient(api_key="test_key")
    
    # Создаем несколько страниц результатов
    page1_data = {
        'backlinks': [{'source_domain': f'domain{i}.com', 'dr': i} for i in range(1000)],
        'total': 2500
    }
    page2_data = {
        'backlinks': [{'source_domain': f'domain{i}.com', 'dr': i} for i in range(1000, 2000)],
        'total': 2500
    }
    page3_data = {
        'backlinks': [{'source_domain': f'domain{i}.com', 'dr': i} for i in range(2000, 2500)],
        'total': 2500
    }
    
    call_count = 0
    async def mock_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return page1_data
        elif call_count == 2:
            return page2_data
        else:
            return page3_data
    
    with patch.object(client, '_make_request', new=mock_request):
        backlinks = await client.get_backlinks("target.com", limit=2500)
        
        assert len(backlinks) == 2500
        assert call_count == 3  # Должно быть 3 запроса для пагинации
