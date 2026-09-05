@echo off
title Refresh Training Data
cd /d "%~dp0"
venv\Scripts\python.exe run_pipeline.py
echo.
pause