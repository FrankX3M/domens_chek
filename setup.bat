@echo off
REM ===================================================================
REM Domain Backlink Analyzer - Setup Script (Windows)
REM ===================================================================

echo ========================================================================
echo   Domain Backlink Analyzer - Установка и настройка
echo ========================================================================
echo.

REM Проверка Python версии
echo [1/5] Проверка Python версии...
python --version
if errorlevel 1 (
    echo Ошибка: Python не найден. Установите Python 3.8 или выше.
    pause
    exit /b 1
)
echo.

REM Создание виртуального окружения
echo [2/5] Создание виртуального окружения...
if exist venv (
    echo Виртуальное окружение уже существует, пропуск...
) else (
    python -m venv venv
    echo Виртуальное окружение создано
)
echo.

REM Активация виртуального окружения
echo [3/5] Активация виртуального окружения...
call venv\Scripts\activate.bat
echo Виртуальное окружение активировано
echo.

REM Установка зависимостей
echo [4/5] Установка зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Зависимости установлены
echo.

REM Создание .env файла
echo [5/5] Настройка переменных окружения...
if exist .env (
    echo Файл .env уже существует, пропуск...
) else (
    copy .env.example .env
    echo Создан файл .env из .env.example
    echo.
    echo ВАЖНО: Отредактируйте файл .env и укажите ваши API ключи:
    echo    - KEYS_SO_API_KEY
    echo    - WHOIS_API_KEY
)
echo.

REM Создание директории для данных
echo Создание директории для данных...
if not exist data mkdir data
echo Директория data создана
echo.

echo ========================================================================
echo   Установка завершена!
echo ========================================================================
echo.
echo Следующие шаги:
echo   1. Активируйте виртуальное окружение:
echo      venv\Scripts\activate
echo.
echo   2. Отредактируйте файл .env и укажите ваши API ключи:
echo      notepad .env
echo.
echo   3. Запустите анализ:
echo      python domain_analyzer.py example.com
echo.
echo Для получения справки:
echo   python domain_analyzer.py --help
echo.
pause
