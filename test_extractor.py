"""
Тесты для модуля извлечения доменов
"""
import pytest
from unittest.mock import MagicMock


class MockBacklink:
    """Мок-объект для тестирования"""
    def __init__(self, source_url: str, target_url: str, source_domain: str, dr: int = None):
        self.source_url = source_url
        self.target_url = target_url
        self.source_domain = source_domain
        self.dr = dr


def test_extract_root_domain():
    """Тест извлечения корневого домена"""
    # Импортируем только для тестов
    import sys
    sys.path.insert(0, '/home/claude')
    from extractor import DomainExtractor
    
    extractor = DomainExtractor()
    
    # Базовые случаи
    assert extractor.get_root_domain("example.com") == "example.com"
    assert extractor.get_root_domain("www.example.com") == "example.com"
    assert extractor.get_root_domain("blog.example.com") == "example.com"
    
    # Домены второго уровня
    assert extractor.get_root_domain("test.co.uk") == "test.co.uk"
    assert extractor.get_root_domain("www.test.co.uk") == "test.co.uk"
    
    # С протоколом
    assert extractor.get_root_domain("https://example.com") == "example.com"
    assert extractor.get_root_domain("http://www.example.com/path") == "example.com"
    
    print("✓ Все тесты extract_root_domain пройдены")


def test_extract_unique_domains():
    """Тест извлечения уникальных доменов"""
    import sys
    sys.path.insert(0, '/home/claude')
    from extractor import DomainExtractor
    
    extractor = DomainExtractor()
    
    backlinks = [
        MockBacklink(
            source_url="https://blog.example.com/post1",
            target_url="https://target.com",
            source_domain="blog.example.com",
            dr=45
        ),
        MockBacklink(
            source_url="https://www.example.com/post2",
            target_url="https://target.com",
            source_domain="www.example.com",
            dr=50
        ),
        MockBacklink(
            source_url="https://another.com",
            target_url="https://target.com",
            source_domain="another.com",
            dr=30
        ),
    ]
    
    domains = extractor.extract_unique_domains(backlinks)
    
    # Должно быть 2 уникальных домена
    assert len(domains) == 2, f"Ожидалось 2 домена, получено {len(domains)}"
    
    # Проверяем нормализацию
    normalized = [d['normalized_domain'] for d in domains]
    assert "example.com" in normalized
    assert "another.com" in normalized
    
    # Проверяем DR (должен быть максимальный)
    example_domain = next(d for d in domains if d['normalized_domain'] == "example.com")
    assert example_domain['dr'] == 50, f"Ожидался DR=50, получен {example_domain['dr']}"
    assert example_domain['backlink_count'] == 2, f"Ожидалось 2 ссылки, получено {example_domain['backlink_count']}"
    
    print("✓ Все тесты extract_unique_domains пройдены")


def test_domain_info_structure():
    """Тест структуры данных DomainInfo"""
    import sys
    sys.path.insert(0, '/home/claude')
    from extractor import DomainExtractor
    
    extractor = DomainExtractor()
    
    domain_info = extractor._extract_domain_info("https://blog.example.com/path", dr=42)
    
    # Проверяем наличие всех полей
    assert 'original_domain' in domain_info
    assert 'normalized_domain' in domain_info
    assert 'tld' in domain_info
    assert 'sld' in domain_info
    assert 'subdomain' in domain_info
    assert 'dr' in domain_info
    assert 'backlink_count' in domain_info
    assert 'is_spam' in domain_info
    assert 'is_registered' in domain_info
    
    # Проверяем значения
    assert domain_info['normalized_domain'] == "example.com"
    assert domain_info['tld'] == "com"
    assert domain_info['sld'] == "example"
    assert domain_info['subdomain'] == "blog"
    assert domain_info['dr'] == 42
    
    print("✓ Все тесты domain_info_structure пройдены")


def test_second_level_domains():
    """Тест обработки доменов второго уровня"""
    import sys
    sys.path.insert(0, '/home/claude')
    from extractor import DomainExtractor
    
    extractor = DomainExtractor()
    
    # Тестируем различные домены второго уровня
    test_cases = [
        ("example.co.uk", "example.co.uk"),
        ("www.example.co.uk", "example.co.uk"),
        ("blog.example.co.uk", "example.co.uk"),
        ("test.com.au", "test.com.au"),
        ("site.co.nz", "site.co.nz"),
    ]
    
    for input_domain, expected in test_cases:
        result = extractor.get_root_domain(input_domain)
        assert result == expected, f"Для {input_domain} ожидалось {expected}, получено {result}"
    
    print("✓ Все тесты second_level_domains пройдены")


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 70)
    print("Запуск тестов для DomainExtractor")
    print("=" * 70)
    
    try:
        test_extract_root_domain()
        test_extract_unique_domains()
        test_domain_info_structure()
        test_second_level_domains()
        
        print("=" * 70)
        print("✓ Все тесты успешно пройдены!")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ Тест провален: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении теста: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
