@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0venv\Scripts\checkin_app.py" %*
