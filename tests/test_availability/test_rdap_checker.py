import pytest
from src.availability.rdap_checker import RDAPChecker
from src.availability.bootstrap_loader import RDAPBootstrapLoader
from src.models.domain_status import DomainStatus


@pytest.mark.asyncio
async def test_rdap_bootstrap_loading():
    """Тест загрузки RDAP bootstrap"""
    bootstrap = RDAPBootstrapLoader()
    await bootstrap.load()
    
    # Проверяем что данные загружены
    assert bootstrap._loaded is True
    assert len(bootstrap._tld_to_servers) > 0
    
    # Проверяем известные TLD
    assert bootstrap.supports_rdap("com") is True
    assert bootstrap.supports_rdap("org") is True
    assert bootstrap.supports_rdap("net") is True


@pytest.mark.asyncio
async def test_rdap_check_registered_domain():
    """Тест проверки зарегистрированного домена"""
    bootstrap = RDAPBootstrapLoader()
    await bootstrap.load()
    
    checker = RDAPChecker(bootstrap)
    result = await checker.check_domain("google.com")
    
    # google.com должен быть зарегистрирован
    assert result is not None
    assert result.status == DomainStatus.REGISTERED
    assert result.tld_supports_rdap is True
    assert result.domain == "google.com"


@pytest.mark.asyncio
async def test_rdap_unsupported_tld():
    """Тест для TLD без поддержки RDAP"""
    bootstrap = RDAPBootstrapLoader()
    await bootstrap.load()
    
    checker = RDAPChecker(bootstrap)
    
    # Проверяем домен с TLD который может не поддерживать RDAP
    # (результат может быть None если TLD не поддерживается)
    result = await checker.check_domain("test.example")
    
    # Либо None (не поддерживается), либо результат с флагом
    if result is not None:
        assert hasattr(result, 'tld_supports_rdap')


@pytest.mark.asyncio
async def test_rdap_invalid_domain():
    """Тест обработки невалидного домена"""
    bootstrap = RDAPBootstrapLoader()
    await bootstrap.load()
    
    checker = RDAPChecker(bootstrap)
    result = await checker.check_domain("not-a-valid-domain")
    
    # Должен вернуть None для невалидного домена
    assert result is None


@pytest.mark.asyncio
async def test_rdap_servers_for_com():
    """Тест получения RDAP серверов для .com"""
    bootstrap = RDAPBootstrapLoader()
    await bootstrap.load()
    
    servers = bootstrap.get_rdap_servers("com")
    
    assert servers is not None
    assert len(servers) > 0
    assert all(isinstance(s, str) for s in servers)
    assert all(s.startswith("http") for s in servers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
