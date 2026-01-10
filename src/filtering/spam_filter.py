"""
Фильтрация доменов по спам-фразам в анкорах и управление исключениями
"""

import re
from pathlib import Path
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class SpamFilter:
    """Фильтрация доменов по спам-фразам в анкорах"""
    
    def __init__(self, spam_phrases_file: str = "data/spam_phrases.txt"):
        self.spam_phrases_file = Path(spam_phrases_file)
        self.spam_phrases: Set[str] = set()
        self._loaded = False
    
    def load_spam_phrases(self) -> None:
        """Загрузка спам-фраз из файла"""
        if self._loaded:
            return
        
        if not self.spam_phrases_file.exists():
            logger.warning(
                f"Файл спам-фраз не найден: {self.spam_phrases_file}. "
                "Фильтрация спама будет пропущена."
            )
            self._loaded = True
            return
        
        try:
            with open(self.spam_phrases_file, 'r', encoding='utf-8') as f:
                for line in f:
                    phrase = line.strip().lower()
                    if phrase and not phrase.startswith('#'):  # Игнорируем комментарии
                        self.spam_phrases.add(phrase)
            
            logger.info(
                f"Загружено {len(self.spam_phrases)} спам-фраз из "
                f"{self.spam_phrases_file}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка загрузки спам-фраз: {e}")
        
        self._loaded = True
    
    def is_spam_anchor(self, anchor_text: Optional[str]) -> bool:
        """
        Проверка анкора на наличие спам-фраз
        
        Args:
            anchor_text: Текст анкора
            
        Returns:
            True если анкор содержит спам-фразы
        """
        if not anchor_text:
            return False
        
        if not self._loaded:
            self.load_spam_phrases()
        
        if not self.spam_phrases:
            return False  # Нет спам-фраз для проверки
        
        # Нормализуем анкор
        normalized = anchor_text.lower().strip()
        
        # Проверяем каждую спам-фразу
        for spam_phrase in self.spam_phrases:
            # Проверка точного совпадения слова (word boundary)
            pattern = r'\b' + re.escape(spam_phrase) + r'\b'
            if re.search(pattern, normalized):
                logger.debug(
                    f"Спам-фраза '{spam_phrase}' найдена в анкоре: "
                    f"'{anchor_text[:50]}...'"
                )
                return True
        
        return False
    
    def filter_backlinks(
        self,
        backlinks: List
    ) -> tuple:
        """
        Фильтрация обратных ссылок по спам-анкорам
        
        Args:
            backlinks: Список всех обратных ссылок
            
        Returns:
            Кортеж (чистые_ссылки, спам_ссылки)
        """
        if not self._loaded:
            self.load_spam_phrases()
        
        clean_backlinks = []
        spam_backlinks = []
        
        for backlink in backlinks:
            anchor = getattr(backlink, 'anchor_text', None)
            if self.is_spam_anchor(anchor):
                spam_backlinks.append(backlink)
            else:
                clean_backlinks.append(backlink)
        
        if backlinks:
            spam_percentage = len(spam_backlinks) / len(backlinks) * 100
            logger.info(
                f"Фильтрация завершена: "
                f"{len(clean_backlinks)} чистых, "
                f"{len(spam_backlinks)} спам ({spam_percentage:.1f}%)"
            )
        
        return clean_backlinks, spam_backlinks
    
    def get_spam_examples(
        self,
        backlinks: List,
        max_examples: int = 5
    ) -> List[str]:
        """
        Получение примеров спам-анкоров
        
        Args:
            backlinks: Список обратных ссылок
            max_examples: Максимум примеров
            
        Returns:
            Список примеров спам-анкоров
        """
        spam_examples = []
        
        for backlink in backlinks:
            anchor = getattr(backlink, 'anchor_text', None)
            if self.is_spam_anchor(anchor):
                spam_examples.append(anchor)
                
                if len(spam_examples) >= max_examples:
                    break
        
        return spam_examples


class DomainExcluder:
    """Управление исключениями доменов"""
    
    def __init__(self, excluded_domains_file: str = "data/excluded_domains.txt"):
        self.excluded_domains_file = Path(excluded_domains_file)
        self.excluded_domains: Set[str] = set()
        self._loaded = False
    
    def load_excluded_domains(self) -> None:
        """Загрузка списка исключенных доменов"""
        if self._loaded:
            return
        
        if not self.excluded_domains_file.exists():
            logger.info(
                f"Файл исключений не найден: {self.excluded_domains_file}. "
                "Исключения не будут применяться."
            )
            self._loaded = True
            return
        
        try:
            with open(self.excluded_domains_file, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain and not domain.startswith('#'):
                        self.excluded_domains.add(domain)
            
            logger.info(
                f"Загружено {len(self.excluded_domains)} исключенных доменов"
            )
            
        except Exception as e:
            logger.error(f"Ошибка загрузки исключений: {e}")
        
        self._loaded = True
    
    def is_excluded(self, domain: str) -> bool:
        """
        Проверка домена на исключение
        
        Args:
            domain: Доменное имя
            
        Returns:
            True если домен в списке исключений
        """
        if not self._loaded:
            self.load_excluded_domains()
        
        return domain.lower() in self.excluded_domains
    
    def add_exclusion(self, domain: str) -> None:
        """
        Добавить домен в список исключений
        
        Args:
            domain: Доменное имя
        """
        if not self._loaded:
            self.load_excluded_domains()
        
        self.excluded_domains.add(domain.lower())
        logger.info(f"Домен {domain} добавлен в исключения")
    
    def remove_exclusion(self, domain: str) -> bool:
        """
        Удалить домен из списка исключений
        
        Args:
            domain: Доменное имя
            
        Returns:
            True если домен был удален
        """
        if not self._loaded:
            self.load_excluded_domains()
        
        domain_lower = domain.lower()
        if domain_lower in self.excluded_domains:
            self.excluded_domains.remove(domain_lower)
            logger.info(f"Домен {domain} удален из исключений")
            return True
        
        return False
    
    def save_exclusions(self) -> None:
        """Сохранить список исключений в файл"""
        try:
            # Создаем директорию если не существует
            self.excluded_domains_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.excluded_domains_file, 'w', encoding='utf-8') as f:
                f.write("# Список исключенных доменов (один на строку)\n")
                f.write("# Комментарии начинаются с #\n\n")
                
                for domain in sorted(self.excluded_domains):
                    f.write(f"{domain}\n")
            
            logger.info(
                f"Сохранено {len(self.excluded_domains)} исключений в "
                f"{self.excluded_domains_file}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка сохранения исключений: {e}")
