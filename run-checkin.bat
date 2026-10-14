@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0app\checkin_app.py" %*
