@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
echo ===== %date% %time% ===== >> logs\task_output.log
venv\Scripts\python.exe src\run_pipeline.py >> logs\task_output.log 2>&1
set EXITCODE=%errorlevel%
echo Exit code: %EXITCODE% >> logs\task_output.log
exit /b %EXITCODE%