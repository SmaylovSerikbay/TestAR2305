@echo off
chcp 65001 >nul
title Web AR - Запуск сервера

echo.
echo ========================================
echo 🚀 Запуск веб-AR приложения
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден!
    echo.
    echo 💡 Установите Python с https://python.org
    echo    Убедитесь, что Python добавлен в PATH
    echo.
    pause
    exit /b 1
)

REM Проверяем наличие необходимых файлов
if not exist "index.html" (
    echo ❌ Файл index.html не найден!
    echo 💡 Убедитесь, что вы находитесь в правильной папке
    pause
    exit /b 1
)

if not exist "ar-app.js" (
    echo ❌ Файл ar-app.js не найден!
    pause
    exit /b 1
)

echo ✅ Файлы найдены!
echo.
echo 📄 Доступные страницы:
echo    • Базовая версия: http://localhost:8000/index.html
if exist "advanced.html" (
    echo    • Продвинутая версия: http://localhost:8000/advanced.html
)
echo.
echo 🌐 Автоматически откроется браузер...
echo 🔴 Для остановки нажмите Ctrl+C
echo.

REM Запускаем Python сервер
if exist "start_server.py" (
    echo 🐍 Запуск через Python скрипт...
    python start_server.py
) else (
    echo 🐍 Запуск стандартного HTTP сервера...
    python -m http.server 8000
)

pause 