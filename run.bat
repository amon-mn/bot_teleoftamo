@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
call .venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8
python -u -m src.main 2>&1 | powershell -NoProfile -Command "$input | ForEach-Object { $_; Add-Content -Path 'logs\run_stdout.log' -Value $_ -Encoding utf8 }"
