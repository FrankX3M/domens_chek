#!/usr/bin/env python3
"""
Скрипт для визуализации структуры проекта
"""

import os
from pathlib import Path


def print_tree(directory, prefix="", ignore_dirs=None, ignore_files=None):
    """Рекурсивный вывод дерева директорий"""
    if ignore_dirs is None:
        ignore_dirs = {'__pycache__', '.pytest_cache', '.mypy_cache', 
                      'venv', 'env', '.git', '.tld_cache', 'htmlcov',
                      '.eggs', 'build', 'dist', '*.egg-info'}
    
    if ignore_files is None:
        ignore_files = {'.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', 
                       '*.db', '*.db-journal'}
    
    try:
        entries = sorted(Path(directory).iterdir(), 
                        key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return
    
    dirs = [e for e in entries if e.is_dir() and e.name not in ignore_dirs]
    files = [e for e in entries if e.is_file() and e.name not in ignore_files]
    
    # Печать файлов
    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1 and len(dirs) == 0)
        connector = "└── " if is_last_file else "├── "
        print(f"{prefix}{connector}{file.name}")
    
    # Печать директорий
    for i, dir_path in enumerate(dirs):
        is_last = i == len(dirs) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{dir_path.name}/")
        
        extension = "    " if is_last else "│   "
        print_tree(dir_path, prefix + extension, ignore_dirs, ignore_files)


def main():
    print("=" * 70)
    print("  DOMAIN BACKLINK ANALYZER - СТРУКТУРА ПРОЕКТА")
    print("=" * 70)
    print()
    print("domain-backlink-analyzer/")
    print_tree(".", "")
    print()
    print("=" * 70)
    print("  СТАТИСТИКА")
    print("=" * 70)
    
    # Подсчет файлов
    py_files = list(Path('.').rglob('*.py'))
    py_files = [f for f in py_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
    
    print(f"  Python файлов: {len(py_files)}")
    print(f"  Тестовых файлов: {len([f for f in py_files if 'test_' in f.name])}")
    print(f"  Модулей: {len([f for f in py_files if '__init__.py' not in f.name and 'test_' not in f.name])}")
    
    # Подсчет строк кода
    total_lines = 0
    for py_file in py_files:
        try:
            with open(py_file, 'r') as f:
                total_lines += len(f.readlines())
        except:
            pass
    
    print(f"  Всего строк кода: {total_lines}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
