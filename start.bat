@echo off
chcp 65001 > nul
echo ========================================
echo Запуск SPH - Сервис проверки хостов
echo ========================================
echo.

echo [1/3] Запуск Backend...
cd restApi
start "SPH Backend" cmd /k "python main.py"

timeout /t 3 > nul

echo [2/3] Запуск Agent...
start "SPH Agent" cmd /k "python run_agent.py"

timeout /t 3 > nul

echo [3/3] Запуск Frontend...
cd ..
start "SPH Frontend" cmd /k "python -m http.server 8080"

timeout /t 3 > nul

echo.
echo ========================================
echo Все сервисы запущены!
echo.
echo Откройте в браузере:
echo http://localhost:8080/html/index.html
echo.
echo Нажмите любую клавишу чтобы открыть браузер...
pause > nul

start http://localhost:8080/html/index.html

echo.
echo ========================================
echo Сервисы работают в отдельных окнах.
echo Закройте их когда закончите работу.
echo ========================================

