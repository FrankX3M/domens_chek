#!/usr/bin/env python3
"""
Демонстрация работы Этапа 2: Обработка и нормализация доменов
Этот скрипт можно запустить независимо для тестирования функционала
"""
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockBacklink:
    """Мок-объект для демонстрации"""
    def __init__(self, source_url: str, target_url: str, source_domain: str, dr: int = None):
        self.source_url = source_url
        self.target_url = target_url
        self.source_domain = source_domain
        self.dr = dr


def main():
    """Демонстрация работы DomainExtractor"""
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ ЭТАПА 2: Обработка и нормализация доменов")
    print("=" * 70)
    print()
    
    # Импортируем наши модули
    sys.path.insert(0, '/home/claude')
    from extractor import DomainExtractor
    from normalizer import DomainNormalizer
    
    # Создаем тестовые данные
    print("1. Создание тестовых обратных ссылок...")
    backlinks = [
        MockBacklink(
            source_url="https://blog.example.com/article1",
            target_url="https://target-site.com",
            source_domain="blog.example.com",
            dr=45
        ),
        MockBacklink(
            source_url="https://www.example.com/page",
            target_url="https://target-site.com",
            source_domain="www.example.com",
            dr=50
        ),
        MockBacklink(
            source_url="https://another-site.com",
            target_url="https://target-site.com",
            source_domain="another-site.com",
            dr=30
        ),
        MockBacklink(
            source_url="https://test.co.uk/page",
            target_url="https://target-site.com",
            source_domain="test.co.uk",
            dr=38
        ),
        MockBacklink(
            source_url="https://www.test.co.uk/another",
            target_url="https://target-site.com",
            source_domain="www.test.co.uk",
            dr=42
        ),
    ]
    print(f"   ✓ Создано {len(backlinks)} тестовых ссылок")
    print()
    
    # Демонстрация нормализации
    print("2. Демонстрация нормализации доменов...")
    test_domains = [
        "HTTPS://WWW.EXAMPLE.COM/PATH",
        "http://m.example.com:8080",
        "https://blog.test.co.uk/page",
    ]
    
    for domain in test_domains:
        normalized = DomainNormalizer.normalize(domain)
        print(f"   {domain:40} → {normalized}")
    print()
    
    # Извлечение уникальных доменов
    print("3. Извлечение уникальных доменов...")
    extractor = DomainExtractor()
    unique_domains = extractor.extract_unique_domains(backlinks)
    print(f"   ✓ Извлечено {len(unique_domains)} уникальных доменов")
    print()
    
    # Вывод результатов
    print("4. Результаты обработки:")
    print("-" * 70)
    print(f"{'Домен':<25} {'Ссылок':<10} {'DR':<10} {'TLD':<10}")
    print("-" * 70)
    
    for domain in sorted(unique_domains, key=lambda x: x['backlink_count'], reverse=True):
        print(
            f"{domain['normalized_domain']:<25} "
            f"{domain['backlink_count']:<10} "
            f"{domain['dr'] if domain['dr'] else 'N/A':<10} "
            f"{domain['tld']:<10}"
        )
    print("-" * 70)
    print()
    
    # Статистика
    print("5. Статистика:")
    total_backlinks = len(backlinks)
    unique_count = len(unique_domains)
    reduction = (1 - unique_count / total_backlinks) * 100
    
    domains_with_dr = [d for d in unique_domains if d['dr'] is not None]
    avg_dr = sum(d['dr'] for d in domains_with_dr) / len(domains_with_dr) if domains_with_dr else 0
    max_dr = max((d['dr'] for d in domains_with_dr), default=0)
    
    print(f"   Всего ссылок: {total_backlinks}")
    print(f"   Уникальных доменов: {unique_count}")
    print(f"   Сокращение: {reduction:.1f}%")
    print(f"   Средний DR: {avg_dr:.1f}")
    print(f"   Максимальный DR: {max_dr}")
    print()
    
    # Демонстрация обработки второго уровня доменов
    print("6. Обработка доменов второго уровня:")
    second_level_examples = [
        "example.co.uk",
        "www.example.co.uk",
        "blog.example.co.uk",
    ]
    
    for domain in second_level_examples:
        root = extractor.get_root_domain(domain)
        print(f"   {domain:<30} → {root}")
    print()
    
    print("=" * 70)
    print("✓ Демонстрация завершена успешно!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"❌ Ошибка: {e}")
        sys.exit(1)
