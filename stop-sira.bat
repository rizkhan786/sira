@echo off
echo Stopping SIRA...
docker stop sira-api-dev sira-postgres sira-chromadb sira-llm
echo.
echo SIRA stopped.
