@echo off
title Multi-LLM Gateway - By Ahmed Adel
echo =======================================================
echo    Starting Multi-LLM API Load Balancer...
echo    Developed by: Ahmed Adel 
echo =======================================================
echo.
echo Starting LiteLLM Proxy Server on http://127.0.0.1:4000 ...
echo Press Ctrl+C to stop the server.
echo.

python -m litellm --config config.yaml --port 4000 --host 127.0.0.1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start LiteLLM. 
    echo Please make sure you ran: pip install "litellm[proxy]"
    echo and config.yaml exists in the current directory.
)

pause
