@echo off
title Log Weight
cd /d "%~dp0"
venv\Scripts\python.exe pipeline\log_weight.py
echo.
pause