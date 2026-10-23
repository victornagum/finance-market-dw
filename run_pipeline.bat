@echo off
cd /d C:\PythonProjects\finance-market-dw

venv\Scripts\python.exe src\run_pipeline.py

exit /b %errorlevel%
