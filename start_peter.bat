@echo off
title PETER AI v2.0
color 0A
echo.
echo  ╔══════════════════════════════════════╗
echo  ║      Starting PETER AI v2.0         ║
echo  ╚══════════════════════════════════════╝
echo.
cd C:\peter-ai
call C:\peter-ai\venv-new\Scripts\activate
python start_peter.py
pause