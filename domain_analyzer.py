#!/usr/bin/env python3
"""
Domain Backlink Analyzer
Полный анализ обратных ссылок домена с экспортом результатов
"""

import asyncio
import argparse
import os
from datetime import datetime
from pathlib import Path

from src.api.keys_so_client import KeysSoClient
from src.domain.extractor import DomainExtractor
from src.availability import DomainAvailabilityChecker
from src.filtering import DomainFilteringPipeline
from src.export.csv_exporter import CSVExporter
from src.export.excel_exporter import ExcelExporter
from src.export.json_exporter import JSONExporter
from src.utils.config import APIConfig, LogConfig
from src.utils.logger import setup_logger


async def main():
    """Главная функция"""
    # Парсинг аргументов
    parser = argparse.ArgumentParser(
        description='Domain Backlink Analyzer - Полный анализ обратных ссылок',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s example.com
  %(prog)s example.com -o report.xlsx -f xlsx
  %(prog)s example.com --skip-rdap --verbose
        """
    )
    
    # Обязательные аргументы
    parser.add_argument('domain', help='Домен для анализа (example.com)')
    
    # Опциональные аргументы
    parser.add_argument(
        '--output', '-o',
        help='Путь к выходному файлу (по умолчанию: results_DOMAIN_DATE.csv)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'xlsx', 'json'],
        default='csv',
        help='Формат вывода (по умолчанию: csv)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=100000,
        help='Максимум ссылок для сбора (по умолчанию: 100000)'
    )
    parser.add_argument(
        '--link-type',
        choices=['backlinks', 'outlinks', 'all'],
        default='backlinks',
        help='Тип ссылок для анализа: backlinks (входящие), outlinks (исходящие), all (все)'
    )
    parser.add_argument(
        '--spam-file',
        default='data/spam_phrases.txt',
        help='Путь к файлу со спам-фразами'
    )
    parser.add_argument(
        '--exclude-file',
        default='data/excluded_domains.txt',
        help='Путь к файлу с исключениями'
    )
    parser.add_argument(
        '--skip-rdap',
        action='store_true',
        help='Пропустить RDAP, использовать только WHOIS API'
    )
    parser.add_argument(
        '--skip-metrics',
        action='store_true',
        help='Не собирать дополнительные метрики'
    )
    parser.add_argument(
        '--only-available',
        action='store_true',
        help='Показать только свободные домены (AVAILABLE)'
    )
    parser.add_argument(
        '--include-spam',
        action='store_true',
        help='Включить спам-домены в отчет'
    )
    parser.add_argument(
        '--include-excluded',
        action='store_true',
        help='Включить исключенные домены в отчет'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=20,
        help='Макс. параллельных запросов (по умолчанию: 20)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод (DEBUG уровень)'
    )
    parser.add_argument(
        '--log-file',
        help='Путь к файлу логов'
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    log_config = LogConfig.from_env()
    if args.verbose:
        log_config.level = "DEBUG"
    if args.log_file:
        log_config.file = args.log_file
    logger = setup_logger(log_config)
    
    # Заголовок
    logger.info("=" * 70)
    logger.info("Domain Backlink Analyzer v1.0")
    logger.info("=" * 70)
    logger.info(f"Целевой домен: {args.domain}")
    logger.info(f"Формат вывода: {args.format.upper()}")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    try:
        api_config = APIConfig.from_env()
        
        async with KeysSoClient(
            api_key=api_config.api_key,
            base_url=api_config.base_url,
            timeout=api_config.timeout,
            max_retries=api_config.max_retries
        ) as api_client:
            
            # ЭТАП 1: Сбор ссылок
            logger.info("")
            all_links = []

            if args.link_type in ['backlinks', 'all']:
                logger.info("[1/5] Сбор входящих ссылок (backlinks)...")
                backlinks = await api_client.get_backlinks(
                    domain=args.domain,
                    limit=args.limit
                )
                logger.info(f"✓ Получено входящих ссылок: {len(backlinks)}")
                all_links.extend(backlinks)

            if args.link_type in ['outlinks', 'all']:
                logger.info("[1/5] Сбор исходящих ссылок (outlinks)...")
                outlinks = await api_client.get_all_outlinks(
                    domain=args.domain,
                    limit=args.limit
                )
                logger.info(f"✓ Получено исходящих ссылок: {len(outlinks)}")
                all_links.extend(outlinks)

            logger.info(f"✓ Всего ссылок собрано: {len(all_links)}")
            
            # ЭТАП 2: Извлечение уникальных доменов
            logger.info("")
            logger.info("[2/5] Извлечение уникальных доменов...")
            extractor = DomainExtractor()
            unique_domains = extractor.extract_unique_domains(all_links)
            logger.info(f"✓ Уникальных доменов: {len(unique_domains)}")
            
            # ЭТАП 3: Проверка доступности
            logger.info("")
            logger.info("[3/5] Проверка доступности (RDAP/WHOIS)...")
            checker = DomainAvailabilityChecker(
                whois_api_key=os.getenv('WHOIS_API_KEY'),
                whois_provider=os.getenv('WHOIS_API_PROVIDER', 'whoisxml'),
                max_concurrent=args.max_workers,
                skip_rdap=args.skip_rdap
            )
            check_results = await checker.check_domains(unique_domains)
            logger.info(f"✓ Проверено доменов: {len(check_results)}")
            
            # ЭТАП 4: Фильтрация и сбор метрик
            logger.info("")
            logger.info("[4/5] Фильтрация и сбор метрик...")
            pipeline = DomainFilteringPipeline(
                spam_phrases_file=args.spam_file,
                excluded_domains_file=args.exclude_file,
                fetch_metrics=not args.skip_metrics,
                api_client=api_client
            )
            
            final_domains = await pipeline.process_domains(
                domains=unique_domains,
                availability_results=check_results,
                backlinks=all_links
            )
            
            # ЭТАП 5: Экспорт
            logger.info("")
            logger.info("[5/5] Экспорт результатов...")
            
            # Определяем имя файла
            if args.output:
                output_file = args.output
            else:
                safe_domain = args.domain.replace('.', '_').replace('/', '_')
                date_str = datetime.now().strftime("%Y-%m-%d")
                output_file = f"output/results_{safe_domain}_{date_str}.{args.format}"
            
            # Экспорт в выбранном формате
            if args.format == 'csv':
                result_file = CSVExporter.export(
                    final_domains,
                    output_file,
                    include_spam=args.include_spam,
                    include_excluded=args.include_excluded,
                    only_available=args.only_available
                )
            elif args.format == 'xlsx':
                result_file = ExcelExporter.export(
                    final_domains,
                    output_file,
                    include_spam=args.include_spam,
                    include_excluded=args.include_excluded,
                    target_domain=args.domain
                )
            elif args.format == 'json':
                result_file = JSONExporter.export(
                    final_domains,
                    output_file,
                    include_spam=args.include_spam,
                    include_excluded=args.include_excluded,
                    target_domain=args.domain
                )
            
            # Финальная статистика
            end_time = datetime.now()
            duration = end_time - start_time
            
            valid_domains = [d for d in final_domains if d.is_valid]
            
            logger.info("")
            logger.info("=" * 70)
            logger.info("✓ Анализ завершен успешно!")
            logger.info("")
            logger.info(f"Результаты сохранены: {result_file}")
            logger.info("")
            logger.info("Статистика:")
            logger.info(f"  ├─ Всего ссылок собрано: {len(all_links)}")
            logger.info(f"  ├─ Уникальных доменов: {len(unique_domains)}")
            logger.info(f"  ├─ Зарегистрированных: {sum(1 for r in check_results if r.status.value == 'REGISTERED')}")
            logger.info(f"  ├─ Свободных (AVAILABLE): {sum(1 for r in check_results if r.status.value == 'AVAILABLE')}")
            logger.info(f"  ├─ Валидных в отчете: {len(valid_domains)}")
            logger.info(f"  └─ Время выполнения: {duration.total_seconds():.1f}s")
            logger.info("=" * 70)
            
    except KeyboardInterrupt:
        logger.warning("\n❌ Прервано пользователем")
        return 130
        
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
