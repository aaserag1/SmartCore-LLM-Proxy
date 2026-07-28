@echo off
setlocal
pushd "%~dp0"

set "SMARTCORE_PYTHON=python"
set "SMARTCORE_PYTHON_ARGS="
python --version >nul 2>nul
if errorlevel 1 (
    set "SMARTCORE_PYTHON=%LocalAppData%\Programs\Python\Launcher\py.exe"
    set "SMARTCORE_PYTHON_ARGS=-3"
)

if not "%SMARTCORE_PYTHON%"=="python" if not exist "%SMARTCORE_PYTHON%" (
    echo [ERROR] Python was not found.
    echo Install Python 3.10 or newer, then try again.
    popd
    exit /b 1
)

"%SMARTCORE_PYTHON%" %SMARTCORE_PYTHON_ARGS% scripts\start_proxy.py %*
set "SMARTCORE_EXIT_CODE=%errorlevel%"

if not "%SMARTCORE_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] SmartCore could not start. Review the message above.
    pause
)

popd
exit /b %SMARTCORE_EXIT_CODE%
