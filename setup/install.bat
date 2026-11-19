@echo off
cd /d "%~dp0.."
title Kaban Key Bot - Установка
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set "PY="

echo ========================================
echo   KABAN KEY BOT - УСТАНОВКА
echo ========================================
echo.

:: Поиск Python
py -3.13 -c "import sys" >nul 2>nul && set "PY=py -3.13" && goto found
py -3.12 -c "import sys" >nul 2>nul && set "PY=py -3.12" && goto found
py -3.11 -c "import sys" >nul 2>nul && set "PY=py -3.11" && goto found
py -3.10 -c "import sys" >nul 2>nul && set "PY=py -3.10" && goto found
python -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,14) else 1)" >nul 2>nul && set "PY=python" && goto found

echo [ERROR] Не найден Python 3.10-3.14.
echo Скачайте Python с https://www.python.org/downloads/windows/
echo Обязательно поставьте галочку "Add python.exe to PATH" при установке!
echo.
pause
exit /b

:found
echo Используется Python:
%PY% --version
echo.

:: Установка библиотек
echo Установка необходимых библиотек...
%PY% -m pip install --upgrade pip >nul 2>&1
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo.

:: Проверка конфигурации
if not exist ".env" (
    echo.
    echo [!] Файл .env не найден. Создаём шаблон...
    copy .env.example .env >nul
    echo.
    echo ========================================
    echo   ВНИМАНИЕ! Нужно заполнить файл .env
    echo ========================================
    echo.
    echo 1. Откройте файл .env в любой папке с ботом
    echo 2. Вставьте токен вашего бота от @BotFather
    echo 3. Сохраните файл
    echo.
    echo Затем запустите бота: %PY% bot/main.py
    echo.
    pause
    exit /b
)

echo Конфигурация .env уже существует.
echo.

:run
echo Запуск бота...
%PY% bot/main.py
if errorlevel 1 pause
exit /b

:fail
echo.
echo [ERROR] Ошибка установки библиотек. Проверьте интернет и повторите.
pause
exit /b