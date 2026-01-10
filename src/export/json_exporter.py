import json
from pathlib import Path
from typing import List
from datetime import datetime
import logging

from ..models.filtered_domain import FilteredDomain

logger = logging.getLogger(__name__)


class JSONExporter:
    """Экспорт данных в JSON формат"""
    
    @staticmethod
    def export(
        domains: List[FilteredDomain],
        output_file: str,
        include_spam: bool = False,
        include_excluded: bool = False,
        target_domain: str = None
    ) -> str:
        """
        Экспорт доменов в JSON
        
        Args:
            domains: Список доменов
            output_file: Путь к выходному файлу
            include_spam: Включить спам-домены
            include_excluded: Включить исключенные домены
            target_domain: Целевой домен
            
        Returns:
            Путь к созданному файлу
        """
        logger.info(f"Экспорт в JSON: {output_file}")
        
        # Фильтруем домены
        filtered = [
            d for d in domains
            if (include_spam or not d.is_spam) and
               (include_excluded or not d.is_excluded) and
               d.is_registered
        ]
        
        # Формируем структуру
        data = {
            "metadata": {
                "target_domain": target_domain,
                "report_date": datetime.now().isoformat(),
                "total_domains_analyzed": len(domains),
                "valid_domains": len(filtered),
                "spam_domains": sum(1 for d in domains if d.is_spam),
                "excluded_domains": sum(1 for d in domains if d.is_excluded)
            },
            "domains": [
                {
                    "domain": d.domain,
                    "dr": d.dr,
                    "ur": d.ur,
                    "backlink_count": d.backlink_count,
                    "total_backlinks": d.total_backlinks,
                    "referring_domains": d.referring_domains,
                    "organic_traffic": d.organic_traffic,
                    "is_spam": d.is_spam,
                    "is_excluded": d.is_excluded,
                    "spam_anchor_examples": d.spam_anchor_examples,
                    "checked_at": d.checked_at.isoformat() if d.checked_at else None
                }
                for d in filtered
            ]
        }
        
        # Создаем директорию
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Сохранение
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Экспортировано {len(filtered)} доменов в {output_path}")
        return str(output_path)
