@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8
python -m src.main --visible --delay 1.5
echo.
echo Execucao concluida. Feche esta janela quando quiser.
pause
