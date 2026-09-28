@echo off
title CODEX - ALL RED AI TERMINAL
color 0C
chcp 65001 >nul
python "%~dp0codex.py"
if %errorlevel% neq 0 (
    echo.
    echo CODEX exited with an error. Press any key to close...
    pause >nul
)
