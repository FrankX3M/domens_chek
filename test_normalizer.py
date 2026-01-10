"""
Тесты для модуля нормализации доменов
"""
import pytest


def test_remove_protocol():
    """Тест удаления протокола"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    test_cases = [
        ("https://example.com", "example.com"),
        ("http://example.com", "example.com"),
        ("ftp://example.com", "example.com"),
        ("example.com", "example.com"),
    ]
    
    for input_url, expected in test_cases:
        result = DomainNormalizer.normalize(input_url)
        assert result == expected, f"Для {input_url} ожидалось {expected}, получено {result}"
    
    print("✓ Тесты remove_protocol пройдены")


def test_remove_path():
    """Тест удаления пути"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    test_cases = [
        ("example.com/path/to/page", "example.com"),
        ("example.com/", "example.com"),
        ("example.com", "example.com"),
        ("https://example.com/path", "example.com"),
    ]
    
    for input_url, expected in test_cases:
        result = DomainNormalizer.normalize(input_url)
        assert result == expected, f"Для {input_url} ожидалось {expected}, получено {result}"
    
    print("✓ Тесты remove_path пройдены")


def test_remove_port():
    """Тест удаления порта"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    test_cases = [
        ("example.com:8080", "example.com"),
        ("example.com:443", "example.com"),
        ("example.com", "example.com"),
    ]
    
    for input_url, expected in test_cases:
        result = DomainNormalizer.normalize(input_url)
        assert result == expected, f"Для {input_url} ожидалось {expected}, получено {result}"
    
    print("✓ Тесты remove_port пройдены")


def test_remove_prefixes():
    """Тест удаления префиксов"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    test_cases = [
        ("www.example.com", "example.com"),
        ("ww2.example.com", "example.com"),
        ("m.example.com", "example.com"),
        ("mobile.example.com", "example.com"),
        ("example.com", "example.com"),
    ]
    
    for input_url, expected in test_cases:
        result = DomainNormalizer.normalize(input_url)
        assert result == expected, f"Для {input_url} ожидалось {expected}, получено {result}"
    
    print("✓ Тесты remove_prefixes пройдены")


def test_full_normalization():
    """Тест полной нормализации"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    test_cases = [
        ("HTTPS://WWW.EXAMPLE.COM/PATH", "example.com"),
        ("http://m.example.com:8080/page", "example.com"),
        ("https://ww2.example.com/", "example.com"),
        ("  https://www.example.com/  ", "example.com"),
    ]
    
    for input_url, expected in test_cases:
        result = DomainNormalizer.normalize(input_url)
        assert result == expected, f"Для {input_url} ожидалось {expected}, получено {result}"
    
    print("✓ Тесты full_normalization пройдены")


def test_is_valid_domain():
    """Тест валидации доменов"""
    import sys
    sys.path.insert(0, '/home/claude')
    from normalizer import DomainNormalizer
    
    # Валидные домены
    valid_domains = [
        "example.com",
        "sub.example.com",
        "example.co.uk",
        "test-site.com",
    ]
    
    for domain in valid_domains:
        assert DomainNormalizer.is_valid_domain(domain), f"{domain} должен быть валидным"
    
    # Невалидные домены
    invalid_domains = [
        "",
        "a" * 300,  # Слишком длинный
        "example",  # Нет TLD
        "-example.com",  # Начинается с дефиса
        "example-.com",  # Заканчивается дефисом
    ]
    
    for domain in invalid_domains:
        assert not DomainNormalizer.is_valid_domain(domain), f"{domain} должен быть невалидным"
    
    print("✓ Тесты is_valid_domain пройдены")


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 70)
    print("Запуск тестов для DomainNormalizer")
    print("=" * 70)
    
    try:
        test_remove_protocol()
        test_remove_path()
        test_remove_port()
        test_remove_prefixes()
        test_full_normalization()
        test_is_valid_domain()
        
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
