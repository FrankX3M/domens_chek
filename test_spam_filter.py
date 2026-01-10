"""
Тесты для модуля фильтрации спама
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.filtering.spam_filter import SpamFilter, DomainExcluder


class TestSpamFilter:
    """Тесты для SpamFilter"""
    
    def test_spam_detection_basic(self):
        """Тест базового обнаружения спама"""
        spam_filter = SpamFilter()
        
        # Добавляем тестовые фразы
        spam_filter.spam_phrases = {"casino", "viagra"}
        spam_filter._loaded = True
        
        assert spam_filter.is_spam_anchor("Play at our casino") is True
        assert spam_filter.is_spam_anchor("Buy viagra online") is True
        assert spam_filter.is_spam_anchor("Read more about gardening") is False
    
    def test_word_boundary(self):
        """Тест проверки границ слов"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino"}
        spam_filter._loaded = True
        
        # "casino" должно быть отдельным словом
        assert spam_filter.is_spam_anchor("casino") is True
        assert spam_filter.is_spam_anchor("visit casino") is True
        assert spam_filter.is_spam_anchor("casino games") is True
        
        # Не должно срабатывать на части слова
        assert spam_filter.is_spam_anchor("occasion") is False
        assert spam_filter.is_spam_anchor("occasions") is False
    
    def test_case_insensitive(self):
        """Тест нечувствительности к регистру"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino"}
        spam_filter._loaded = True
        
        assert spam_filter.is_spam_anchor("CASINO") is True
        assert spam_filter.is_spam_anchor("Casino") is True
        assert spam_filter.is_spam_anchor("CaSiNo") is True
    
    def test_empty_anchor(self):
        """Тест пустого анкора"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino"}
        spam_filter._loaded = True
        
        assert spam_filter.is_spam_anchor(None) is False
        assert spam_filter.is_spam_anchor("") is False
        assert spam_filter.is_spam_anchor("   ") is False
    
    def test_multiple_spam_phrases(self):
        """Тест множественных спам-фраз"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino", "viagra", "poker"}
        spam_filter._loaded = True
        
        assert spam_filter.is_spam_anchor("play poker online") is True
        assert spam_filter.is_spam_anchor("best casino") is True
        assert spam_filter.is_spam_anchor("buy viagra") is True
    
    def test_load_from_file(self):
        """Тест загрузки из файла"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# Comment line\n")
            f.write("casino\n")
            f.write("viagra\n")
            f.write("\n")  # Пустая строка
            f.write("   poker   \n")  # С пробелами
            temp_file = f.name
        
        try:
            spam_filter = SpamFilter(temp_file)
            spam_filter.load_spam_phrases()
            
            assert len(spam_filter.spam_phrases) == 3
            assert "casino" in spam_filter.spam_phrases
            assert "viagra" in spam_filter.spam_phrases
            assert "poker" in spam_filter.spam_phrases
            
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Тест загрузки несуществующего файла"""
        spam_filter = SpamFilter("nonexistent_file.txt")
        spam_filter.load_spam_phrases()
        
        # Должно загрузиться без ошибок, но с пустым набором фраз
        assert len(spam_filter.spam_phrases) == 0
    
    def test_get_spam_examples(self):
        """Тест получения примеров спама"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino", "poker"}
        spam_filter._loaded = True
        
        # Создаем mock объекты backlinks
        class MockBacklink:
            def __init__(self, anchor):
                self.anchor_text = anchor
        
        backlinks = [
            MockBacklink("visit casino"),
            MockBacklink("play poker"),
            MockBacklink("read article"),
            MockBacklink("casino games"),
            MockBacklink("poker tournament"),
        ]
        
        examples = spam_filter.get_spam_examples(backlinks, max_examples=3)
        
        assert len(examples) == 3
        assert all(
            spam_filter.is_spam_anchor(ex) for ex in examples
        )


class TestDomainExcluder:
    """Тесты для DomainExcluder"""
    
    def test_basic_exclusion(self):
        """Тест базового исключения"""
        excluder = DomainExcluder()
        excluder.excluded_domains = {"facebook.com", "twitter.com"}
        excluder._loaded = True
        
        assert excluder.is_excluded("facebook.com") is True
        assert excluder.is_excluded("twitter.com") is True
        assert excluder.is_excluded("example.com") is False
    
    def test_case_insensitive_exclusion(self):
        """Тест нечувствительности к регистру"""
        excluder = DomainExcluder()
        excluder.excluded_domains = {"facebook.com"}
        excluder._loaded = True
        
        assert excluder.is_excluded("FACEBOOK.COM") is True
        assert excluder.is_excluded("Facebook.com") is True
        assert excluder.is_excluded("FaceBook.COM") is True
    
    def test_add_exclusion(self):
        """Тест добавления исключения"""
        excluder = DomainExcluder()
        excluder._loaded = True
        
        excluder.add_exclusion("example.com")
        assert excluder.is_excluded("example.com") is True
        
        excluder.add_exclusion("ANOTHER.COM")
        assert excluder.is_excluded("another.com") is True
    
    def test_remove_exclusion(self):
        """Тест удаления исключения"""
        excluder = DomainExcluder()
        excluder.excluded_domains = {"facebook.com", "twitter.com"}
        excluder._loaded = True
        
        result = excluder.remove_exclusion("facebook.com")
        assert result is True
        assert excluder.is_excluded("facebook.com") is False
        assert excluder.is_excluded("twitter.com") is True
        
        # Попытка удалить несуществующий домен
        result = excluder.remove_exclusion("nonexistent.com")
        assert result is False
    
    def test_load_from_file(self):
        """Тест загрузки из файла"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# Excluded domains\n")
            f.write("facebook.com\n")
            f.write("twitter.com\n")
            f.write("\n")
            f.write("   linkedin.com   \n")
            temp_file = f.name
        
        try:
            excluder = DomainExcluder(temp_file)
            excluder.load_excluded_domains()
            
            assert len(excluder.excluded_domains) == 3
            assert "facebook.com" in excluder.excluded_domains
            assert "twitter.com" in excluder.excluded_domains
            assert "linkedin.com" in excluder.excluded_domains
            
        finally:
            os.unlink(temp_file)
    
    def test_save_exclusions(self):
        """Тест сохранения исключений"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "exclusions.txt"
            
            excluder = DomainExcluder(str(temp_file))
            excluder.excluded_domains = {"facebook.com", "twitter.com", "google.com"}
            excluder._loaded = True
            
            excluder.save_exclusions()
            
            # Проверяем что файл создан
            assert temp_file.exists()
            
            # Загружаем обратно и проверяем
            excluder2 = DomainExcluder(str(temp_file))
            excluder2.load_excluded_domains()
            
            assert len(excluder2.excluded_domains) == 3
            assert "facebook.com" in excluder2.excluded_domains


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_spam_filter_with_backlinks(self):
        """Тест фильтрации с реальными объектами backlinks"""
        spam_filter = SpamFilter()
        spam_filter.spam_phrases = {"casino", "viagra"}
        spam_filter._loaded = True
        
        class MockBacklink:
            def __init__(self, anchor):
                self.anchor_text = anchor
        
        backlinks = [
            MockBacklink("casino games"),
            MockBacklink("buy viagra"),
            MockBacklink("read article"),
            MockBacklink("best practices"),
            MockBacklink("online casino"),
        ]
        
        clean, spam = spam_filter.filter_backlinks(backlinks)
        
        assert len(clean) == 2
        assert len(spam) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
