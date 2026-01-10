import csv
from pathlib import Path
from typing import List
from datetime import datetime
import logging

from ..models.filtered_domain import FilteredDomain

logger = logging.getLogger(__name__)


class CSVExporter:
    """Экспорт данных в CSV формат"""
    
    @staticmethod
    def export(
        domains: List[FilteredDomain],
        output_file: str,
        include_spam: bool = False,
        include_excluded: bool = False
    ) -> str:
        """
        Экспорт доменов в CSV
        
        Args:
            domains: Список доменов
            output_file: Путь к выходному файлу
            include_spam: Включить спам-домены
            include_excluded: Включить исключенные домены
            
        Returns:
            Путь к созданному файлу
        """
        logger.info(f"Экспорт в CSV: {output_file}")
        
        # Фильтруем домены
        filtered = [
            d for d in domains
            if (include_spam or not d.is_spam) and
               (include_excluded or not d.is_excluded) and
               d.is_registered
        ]
        
        # Создаем директорию если не существует
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Заголовки
        headers = [
            'Domain',
            'DR',
            'UR',
            'Backlink Count',
            'Total Backlinks',
            'Referring Domains',
            'Organic Traffic',
            'Spam Status',
            'Excluded',
            'Checked At'
        ]
        
        # Запись в CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for domain in filtered:
                writer.writerow({
                    'Domain': domain.domain,
                    'DR': domain.dr if domain.dr is not None else '',
                    'UR': domain.ur if domain.ur is not None else '',
                    'Backlink Count': domain.backlink_count,
                    'Total Backlinks': domain.total_backlinks or '',
                    'Referring Domains': domain.referring_domains or '',
                    'Organic Traffic': domain.organic_traffic or '',
                    'Spam Status': 'SPAM' if domain.is_spam else 'CLEAN',
                    'Excluded': 'YES' if domain.is_excluded else 'NO',
                    'Checked At': domain.checked_at.isoformat() if domain.checked_at else ''
                })
        
        logger.info(f"✓ Экспортировано {len(filtered)} доменов в {output_path}")
        return str(output_path)
