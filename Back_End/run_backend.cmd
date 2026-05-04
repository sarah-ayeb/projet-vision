@echo off
REM Start FastAPI with the venv that includes the image pipeline (ultralytics, paddleocr, …)
cd /d "%~dp0"
venv\Scripts\python.exe main.py
