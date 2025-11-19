@echo off
echo Starting SIRA...
echo.
cd ops\docker
docker compose up -d
cd ..\..
echo.
echo Waiting for services to be ready...
timeout /t 20 /nobreak >nul
echo.
echo SIRA is running!
echo.
echo Check Docker Desktop - you should see "sira" project group
echo.
echo Access points:
echo   API Docs:  http://localhost:8080/docs
echo   Health:    http://localhost:8080/health
echo   Metrics:   http://localhost:8080/metrics/summary
