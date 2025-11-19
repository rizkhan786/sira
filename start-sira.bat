@echo off
echo Starting SIRA...
docker start sira-postgres sira-chromadb sira-llm
timeout /t 5 /nobreak >nul
docker start sira-api-dev
echo.
echo Waiting for services to be ready...
timeout /t 20 /nobreak >nul
echo.
echo SIRA is running!
echo.
echo Access points:
echo   API Docs:  http://localhost:8080/docs
echo   Health:    http://localhost:8080/health
echo   Metrics:   http://localhost:8080/metrics/summary
echo.
docker ps --filter "name=sira-" --format "table {{.Names}}\t{{.Status}}"
