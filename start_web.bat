@echo off
echo ================================================================================
echo AGENTIC RAG WEB INTERFACE - STARTUP
echo ================================================================================
echo.
echo Starting backend API server on port 8000...
start cmd /k "python backend_api.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting frontend web server on port 5000...
start cmd /k "python web_server.py"
timeout /t 2 /nobreak >nul
echo.
echo ================================================================================
echo SERVERS STARTED
echo ================================================================================
echo Frontend: http://127.0.0.1:5000
echo Backend:  http://127.0.0.1:8000
echo.
echo Press any key to open browser...
pause >nul
start http://127.0.0.1:5000
