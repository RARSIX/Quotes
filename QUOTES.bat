@echo off
cd C:\Quotes
REM Verificar se o app.exe está em execução
tasklist /FI "IMAGENAME eq app.exe" | find /I "app.exe" >nul

REM Se o app.exe estiver em execução, encerrá-lo
if not errorlevel 1 (
    echo O aplicativo app.exe está em execucao. Encerrando o processo...
    taskkill /F /IM app.exe
    exit /b
)

REM Se o app.exe não estiver em execução, executar o app.exe
echo Iniciando o app.exe...
start "" app.exe

REM Aguardar alguns segundos para garantir que o servidor Flask esteja rodando
timeout /t 3 /nobreak >nul

REM Abrir o navegador na URL do Flask
echo Abrindo o navegador na URL http://127.0.0.1:5000
start http://127.0.0.1:5000

