#!/usr/bin/env python3
"""
Быстрый тест фильтрации
Демонстрирует работу модулей без полного анализа
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from src.filtering.spam_filter import SpamFilter, DomainExcluder


def test_spam_filter():
    """Тест спам-фильтра"""
    print("=" * 60)
    print("Тест SpamFilter")
    print("=" * 60)
    
    spam_filter = SpamFilter("data/spam_phrases.txt")
    spam_filter.load_spam_phrases()
    
    print(f"\nЗагружено спам-фраз: {len(spam_filter.spam_phrases)}")
    print(f"Примеры фраз: {list(spam_filter.spam_phrases)[:5]}")
    
    # Тестовые анкоры
    test_anchors = [
        "Visit our casino online",
        "Read this article",
        "Buy viagra cheap",
        "Learn Python programming",
        "Play poker now",
        "Best practices for SEO",
    ]
    
    print("\nТестирование анкоров:")
    print("-" * 60)
    
    for anchor in test_anchors:
        is_spam = spam_filter.is_spam_anchor(anchor)
        status = "🚫 SPAM" if is_spam else "✅ CLEAN"
        print(f"{status:12s} | {anchor}")
    
    print()


def test_domain_excluder():
    """Тест исключений доменов"""
    print("=" * 60)
    print("Тест DomainExcluder")
    print("=" * 60)
    
    excluder = DomainExcluder("data/excluded_domains.txt")
    excluder.load_excluded_domains()
    
    print(f"\nЗагружено исключений: {len(excluder.excluded_domains)}")
    print(f"Примеры доменов: {list(excluder.excluded_domains)[:5]}")
    
    # Тестовые домены
    test_domains = [
        "facebook.com",
        "example.com",
        "twitter.com",
        "myblog.com",
        "linkedin.com",
        "unknown.com",
    ]
    
    print("\nТестирование доменов:")
    print("-" * 60)
    
    for domain in test_domains:
        is_excluded = excluder.is_excluded(domain)
        status = "🚫 EXCLUDED" if is_excluded else "✅ ALLOWED"
        print(f"{status:15s} | {domain}")
    
    print()


def main():
    """Главная функция"""
    print("\n")
    print("🧪 Быстрый тест модулей фильтрации")
    print("=" * 60)
    print()
    
    try:
        # Тест спам-фильтра
        test_spam_filter()
        
        # Тест исключений
        test_domain_excluder()
        
        print("=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("=" * 60)
        print()
        
    except FileNotFoundError as e:
        print(f"\n❌ Ошибка: Файл не найден - {e}")
        print("   Убедитесь что файлы данных созданы:")
        print("   - data/spam_phrases.txt")
        print("   - data/excluded_domains.txt")
        print()
        return 1
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
